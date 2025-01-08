from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os
from dotenv import load_dotenv
import logging
import random
from difflib import SequenceMatcher  # 類似度計算に使用

# 環境変数の読み込み
load_dotenv()

# Flaskアプリケーションの設定
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}}, supports_credentials=True)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# OpenAI APIキー設定
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise ValueError("APIキーが設定されていません。")

# Akinatorゲームクラス
class AkinatorGame:
    def __init__(self):
        self.messages = []
        self.question_count = 0
        self.max_questions = 25
        self.topic_description = ""  # お題の具体的な名前
        self.topic_category = ""     # お題のカテゴリ（ユーザー向け情報）
        self.game_active = False     # ゲームがアクティブかどうか

    def initialize_game(self):
        """ゲームの初期化 - お題とヒントの生成"""
        if self.game_active:
            logger.warning("ゲームはすでにアクティブです。再初期化はスキップされました。")
            return "ゲームはすでに開始されています。新しいゲームを開始するには、現在のゲームを終了してください。"

        logger.info("ゲームを初期化中...")
        try:
            # カテゴリ選択肢
            available_categories = [
                "実在の有名人（現代または歴史上の人物）",
                "動物（実在の生物）",
                "食べ物や飲み物",
                "場所（国、都市、建造物など）"
            ]
            self.topic_category = random.choice(available_categories)
            logger.info(f"選択されたカテゴリ: {self.topic_category}")

            # お題を生成
            self.topic_description = self.generate_topic_description(self.topic_category)
            if not self.topic_description:
                raise ValueError("お題の生成に失敗しました。")

            logger.info(f"生成されたお題: {self.topic_description}")

            # ゲームの状態をリセット
            self.game_active = True
            self.messages = [
                {"role": "assistant", "content": f"ゲームを開始しました。今回のお題は「{self.topic_category}」です。質問をどうぞ！"}
            ]
            self.question_count = 0

            return self.messages[0]["content"]
        except Exception as e:
            logger.error(f"ゲーム初期化中のエラー: {e}")
            return "ゲームの初期化中にエラーが発生しました。もう一度お試しください。"

    def generate_topic_description(self, category):
        """GPTを使ってカテゴリに基づく具体的なお題を生成"""
        try:
            prompt = f"""
            あなたは「アキネーター」です。
            以下のカテゴリに基づいて、具体的なお題を1つ生成してください。
            - カテゴリ: {category}
            - より多様なお題を生成したいと考えています。
            - ただし、一般人が知っているようなお題を選択してください。
            - 出力形式: [お題の具体的な名前のみ]
            """
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": "お題を生成してください。"}
                ]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error generating topic description: {e}")
            return None

    def generate_hint(self, level):
        """現在のお題に基づいてレベル別のヒントを生成"""
        if not self.game_active:
            return "ゲームは終了しました。新しいゲームを開始してください。"

        try:
            prompt = f"""
            あなたは「アキネーター」です。
            現在のお題は「{self.topic_description}」です。
            ヒントレベル: {level}
            レベルに応じて、以下の内容に従ってヒントを生成してください。
            - 簡単（easy）: 分かりやすい特徴を含む。
            - 普通（medium）: 少し抽象的なヒント。
            - 難しい（hard）: より挑戦的で難しいヒント。
            """
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": "ヒントを生成してください。"}
                ]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error generating hint: {e}")
            return "エラー: ヒントを生成できませんでした。"

    def calculate_similarity(self, user_answer, topic_description):
        """ユーザーの回答とお題の類似度を計算"""
        return SequenceMatcher(None, user_answer.lower(), topic_description.lower()).ratio()

    def check_answer(self, user_answer):
        """プレイヤーの答えを正解と照合"""
        if not self.game_active:
            return "ゲームは終了しました。新しいゲームを開始してください。"

        # 類似度を計算
        similarity = self.calculate_similarity(user_answer, self.topic_description)

        if similarity >= 0.6:  # 類似度が60%以上なら正解とする
            self.game_active = False
            return (
                f"正解です！おめでとうございます！\n"
                f"あなたの回答: 「{user_answer}」\n"
                f"お題: 「{self.topic_description}」\n"
                f"類似度: {int(similarity * 100)}%"
            )
        else:
            return (
                f"残念、正解ではありません。\n"
                f"あなたの回答: 「{user_answer}」\n"
                f"類似度: {int(similarity * 100)}%\n"
                f"もう一度挑戦してください！"
            )

    def chat_with_gpt(self, user_message):
        """ユーザーの質問にGPTで応答"""
        if not self.game_active:
            return "ゲームは終了しました。新しいゲームを開始してください。"

        self.messages.append({"role": "user", "content": user_message})
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=self.messages
            )
            assistant_message = response.choices[0].message.content.strip()
            allowed_responses = ["はい", "いいえ", "部分的にそう", "部分的に違う", "わからない"]
            if any(resp in assistant_message for resp in allowed_responses):
                self.messages.append({"role": "assistant", "content": assistant_message})
                return assistant_message
            else:
                return "すみません、指定された形式の返答ができませんでした。"
        except Exception as e:
            logger.error(f"Error chatting with GPT: {e}")
            return "エラーが発生しました。"

    def give_up(self):
        """プレイヤーがギブアップした場合"""
        if not self.game_active:
            return "ゲームは終了しました。新しいゲームを開始してください。"

        self.game_active = False
        return f"残念！今回のお題は「{self.topic_description}」でした。"

# Flaskルート設定
@app.route('/initialize', methods=['POST'])
def initialize_game():
    message = game_instance.initialize_game()
    return jsonify({"message": message})

@app.route('/chat', methods=['POST'])
def chat_with_gpt():
    message = request.json.get("message")
    response_message = game_instance.chat_with_gpt(message)
    return jsonify({"response": response_message})

@app.route('/check', methods=['POST'])
def check_answer():
    user_answer = request.json.get("answer")
    result = game_instance.check_answer(user_answer)
    return jsonify({"result": result})

@app.route('/hint', methods=['POST'])
def get_hint():
    level = request.json.get("level", "medium")
    hint = game_instance.generate_hint(level)
    return jsonify({"hint": hint})

@app.route('/give_up', methods=['POST'])
def give_up():
    result = game_instance.give_up()
    return jsonify({"result": result})

# サーバーの起動
if __name__ == '__main__':
    game_instance = AkinatorGame()
    app.run(debug=True, port=5001)