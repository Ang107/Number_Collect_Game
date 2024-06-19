import tkinter as tk
from tkinter import messagebox
import random
import copy
from PIL import Image, ImageTk


# 定数の定義
H = 5
W = 5
END_TURN = 24
INF = float("inf")
dx = (0, 0, -1, 1)
dy = (-1, 1, 0, 0)
q_box = [
    "I_multiply_5",
    "I_multiply_2",
    "Y_p_to_0",
    "I_multipy_0.5",
    "I_p_to_0",
    "exchange",
    "point_reset",
    "none",
]
q_weight = [5, 10, 10, 20, 15, 15, 20, 5]
q_str = [
    "自分のスコアを5倍にする",
    "自分のスコアを2倍にする",
    "相手のスコアを0にする",
    "自分のスコアを半分にする",
    "自分のスコアを0にする",
    "自分のスコアと相手のスコアを交換",
    "盤面のポイントをランダムに上書き",
    "しかし何も起こらなかった",
]


class Character:
    def __init__(self, x: int, y: int, game_score: int) -> None:
        self.x = x
        self.y = y
        self.game_score = game_score


class NumberCollectGame:
    def __init__(
        self,
        p1_name: str = "Player_1",
        p2_name: str = "Player_2",
        seed: int = 0,
    ) -> None:
        random.seed(seed)
        self.turn = 0
        # プレイヤーが先手: 0 or 後手: 1
        self.player_turn = random.randrange(2)

        # 初期位置をランダムに決定
        chara_1_x = random.randrange(H)
        chara_1_y = random.randrange(W // 2)
        chara_1 = Character(chara_1_x, chara_1_y, 0)
        chara_2 = Character(H - chara_1_x - 1, W - chara_1_y - 1, 0)
        if self.player_turn == 0:
            self.characters = [chara_1, chara_2]
            self.player_name = [p1_name, p2_name]
        else:
            self.characters = [chara_2, chara_1]
            self.player_name = [p2_name, p1_name]

        # 盤面上の数字をランダムに決定
        self.points = [[0] * W for _ in range(H)]
        for i in range(H):
            for j in range(W):
                if i == self.characters[0].x and j == self.characters[0].y:
                    continue
                if i == self.characters[1].x and j == self.characters[1].y:
                    continue
                self.points[i][j] = random.randrange(10)
        while True:
            x = random.randrange(H)
            y = random.randrange(W)
            if (x != self.characters[0].x or y != self.characters[0].y) and (
                x != self.characters[1].x or y != self.characters[1].y
            ):
                self.points[x][y] = "?"
                break

    def reset(self, player_turn, p1_name, p2_name, seed):
        self.__init__(
            player_turn=player_turn, p1_name=p1_name, p2_name=p2_name, seed=seed
        )

    def isDone(self) -> bool:
        return self.turn == END_TURN

    def isFirstPlayer(self) -> bool:
        return self.turn % 2 == 0

    def getFirstPlayerScoreForWinRate(self) -> int:
        winig_status = self.getWiningStatus()
        if winig_status == "WIN":
            if self.isFirstPlayer():
                return 1
            else:
                return 0
        elif winig_status == "LOSE":
            if self.isFirstPlayer():
                return 0
            else:
                return 1
        else:
            return 0.5

    # 1ターン進める。
    # charactersをswapすることで、常にcharacters[0]が注目するキャラクターとする。
    def advance(self, action: int, search: bool = True) -> None | int:
        q_box_index = None
        character = self.characters[0]
        character.x += dx[action]
        character.y += dy[action]
        point = self.points[character.x][character.y]
        if point == "?":
            if search:
                if self.characters[0].game_score < self.characters[1].game_score:
                    character.game_score += 11
                else:
                    character.game_score += 0
            else:
                q_box_index = random.choices(range(len(q_box)), q_weight)[0]
                q_box_str = q_box[q_box_index]
                # print(q_box_str)
                if q_box_str == "I_multiply_5":
                    self.characters[0].game_score *= 5
                elif q_box_str == "I_multiply_2":
                    self.characters[0].game_score *= 2
                elif q_box_str == "Y_p_to_0":
                    self.characters[1].game_score = 0
                elif q_box_str == "I_multipy_0.5":
                    self.characters[0].game_score //= 2
                elif q_box_str == "I_p_to_0":
                    self.characters[0].game_score = 0
                elif q_box_str == "exchange":
                    self.characters[0].game_score, self.characters[1].game_score = (
                        self.characters[1].game_score,
                        self.characters[0].game_score,
                    )
                elif q_box_str == "point_reset":
                    for i in range(H):
                        for j in range(W):
                            if i == self.characters[0].x and j == self.characters[0].y:
                                continue
                            if i == self.characters[1].x and j == self.characters[1].y:
                                continue
                            self.points[i][j] = random.randrange(10)
                elif q_box_str == "none":
                    pass

                while True:
                    x = random.randrange(H)
                    y = random.randrange(W)
                    if (x != self.characters[0].x or y != self.characters[0].y) and (
                        x != self.characters[1].x or y != self.characters[1].y
                    ):
                        self.points[x][y] = "?"
                        break

        elif point > 0:
            character.game_score += point

        self.points[character.x][character.y] = 0

        self.turn += 1
        self.characters[0], self.characters[1] = self.characters[1], self.characters[0]
        self.player_name[0], self.player_name[1] = (
            self.player_name[1],
            self.player_name[0],
        )
        return q_box_index

    # 合法手を返す。
    def legalActions(self) -> list[int]:
        actions = []
        character = self.characters[0]
        for action in range(4):
            tx = character.x + dx[action]
            ty = character.y + dy[action]
            if (
                0 <= tx
                and tx < H
                and 0 <= ty
                and ty < W
                and (tx != self.characters[1].x or ty != self.characters[1].y)
            ):
                actions.append(action)
        return actions

    # 勝敗状況を返す。
    def getWiningStatus(self) -> str:
        if self.isDone():
            if self.characters[0].game_score > self.characters[1].game_score:
                return "WIN"
            elif self.characters[0].game_score < self.characters[1].game_score:
                return "LOSE"
            else:
                return "DRAW"
        else:
            return ""

    # デバッグ用関数。ゲーム状況をCUIで返す。
    def __str__(self) -> str:
        points = [i[:] for i in self.points]
        result = []
        result.append(f"turn: {self.turn}")
        result.append(f"player_turn: {self.player_turn}")
        for p_id in range(2):
            actual_p_id = (p_id + self.turn) % 2
            character = self.characters[actual_p_id]
            result.append(f"player_name: {self.player_name[actual_p_id]}")
            result.append(f"score: {character.game_score}")
            result.append(f"x: {character.x}, y: {character.y}")
            if p_id == 0:
                points[character.x][character.y] = "A"
            else:
                points[character.x][character.y] = "B"
        result.append("points: ")
        for i in points:
            result.append(f"{' '.join([str(j) for j in i])}")
        result.append("")
        return "\n".join(result)

    # ランダムに行動を決定
    def randomAction(self) -> int:
        legal_actions = self.legalActions()
        return random.choice(legal_actions)

    # 盤面の評価を返す
    def getScore(self) -> int:
        return self.characters[0].game_score - self.characters[1].game_score

    def miniMaxScore(self, depth: int) -> int:
        if self.isDone() or depth == 0:
            return self.getScore()
        legal_actions = self.legalActions()
        # 今のところ不要
        # if len(legal_actions) == 0:
        #     return self.getScore()
        best_score = -INF
        for action in legal_actions:
            next_number_collect_game = copy.deepcopy(self)
            next_number_collect_game.advance(action)
            score = -next_number_collect_game.miniMaxScore(depth - 1)
            if score > best_score:
                best_score = score
        return best_score

    def miniMaxAction(self, depth: int) -> int:
        best_action = -1
        best_score = -INF
        legal_actions = self.legalActions()
        # print(self)
        for action in legal_actions:
            next_number_collect_game = copy.deepcopy(self)
            next_number_collect_game.advance(action)
            score = -next_number_collect_game.miniMaxScore(depth)
            # print(action, dx[action], dy[action], score)
            if score > best_score:
                best_score = score
                best_action = action
        return best_action

    # def isPlayerTurn(self) -> bool:
    #     return self.turn % 2 == self.player_turn

    # CPUが手を選択し、行動する。
    def playNPC(self):
        action = self.miniMaxAction(6)
        return self.advance(action, search=False)

    # プレイヤーが手を選択し、行動する。
    def playUser(self, action):
        return self.advance(action, search=False)

    def checkWinigStatus(self):
        if self.isDone():
            winig_status = self.getWiningStatus()
            if winig_status == "WIN":
                return 0
            elif winig_status == "LOSE":
                return 1
            elif winig_status == "DRAW":
                return 2
        else:
            return None

    # 状況を出力しながらゲームを進行する
    # CUI用
    def playGame(self, ais: list[callable]) -> None:
        # print(self)
        while not self.isDone():
            # 1P
            # print("1p ---------------------")
            # action = self.miniMaxAction(END_TURN)
            action = ais[0]()
            # print(f"action: {action}")
            self.advance(action)
            # print(self)
            if self.isDone():
                winig_status = self.getWiningStatus()
                if winig_status == "WIN":
                    print(f"Winner: {self.player_name[0]}")
                    return f"Winner: {self.player_name[0]}"
                elif winig_status == "LOSE":
                    print(f"Winner: {self.player_name[1]}")
                    return f"Winner: {self.player_name[1]}"
                elif winig_status == "DRAW":
                    print("DRAW")
                    return "DRAW"
                break

            # 2P
            # print("2p ---------------------")
            # action = self.randomAction()
            action = ais[1]()
            # print(f"action: {action}")
            self.advance(action)
            # print(self)
            if self.isDone():
                winig_status = self.getWiningStatus()
                if winig_status == "WIN":
                    print(f"Winner: {self.player_name[0]}")
                    return f"Winner: {self.player_name[0]}"
                elif winig_status == "LOSE":
                    print(f"Winner: {self.player_name[1]}")
                    return f"Winner: {self.player_name[1]}"
                elif winig_status == "DRAW":
                    print("DRAW")
                    return "DRAW"
                break


def testFirstPlayerWinRate(game_num: int = 100):
    first_player_win_num = 0
    first_player_draw_num = 0
    first_player_lose_num = 0
    p1_name = "Player_1"
    p2_name = "Player_2"
    number_collect_game = NumberCollectGame(
        seed=0, p1_name="Player_1", p2_name="Player_2"
    )
    ais = [
        lambda: NumberCollectGame.miniMaxAction(number_collect_game, END_TURN),
        lambda: NumberCollectGame.randomAction(number_collect_game),
    ]
    for i in range(game_num):
        number_collect_game.reset(p1_name, p2_name, i)
        result = number_collect_game.playGame(ais)
        if result == f"Winner: {p1_name}":
            first_player_win_num += 1
        elif result == f"Winner: {p2_name}":
            first_player_lose_num += 1
        else:
            first_player_draw_num += 1

    print(first_player_win_num, first_player_lose_num, first_player_draw_num)
    for i in range(game_num):
        number_collect_game.reset(p1_name, p2_name, i)
        result = number_collect_game.playGame(ais[::-1])
        if result == f"Winner: {p1_name}":
            first_player_lose_num += 1
        elif result == f"Winner: {p2_name}":
            first_player_win_num += 1
        else:
            first_player_draw_num += 1
    print(
        f"win: {first_player_win_num}, lose: {first_player_lose_num}, draw: {first_player_draw_num}"
    )
    print(f"win_rate: {first_player_win_num / (game_num * 2)}")


# testFirstPlayerWinRate(100)
# number_collect_game.playGame()


class NumberCollectGameGUI:
    def __init__(self):
        self.show_start_menu_window()

    def show_start_menu_window(self):
        start_menu_window = tk.Tk()
        start_menu_window.title("スタートメニュー")
        start_menu_window.geometry("600x450")
        start_menu_window.geometry("+100+100")
        start_menu_window.grab_set()
        start_menu_window.protocol("WM_DELETE_WINDOW", self.close)

        rule_button = tk.Button(
            start_menu_window,
            text="遊び方・ルール",
            command=lambda: [start_menu_window.destroy(), self.show_how_to_play()],
            width=28,
            font=("Helvetica", 24),
        )
        rule_button.pack(pady=20)

        solo_play_button = tk.Button(
            start_menu_window,
            text="一人で遊ぶ（NPC対戦）",
            command=lambda: [
                start_menu_window.destroy(),
                self.set_mode(1),
                self.setupGUI(),
            ],
            width=28,
            font=("Helvetica", 24),
        )
        solo_play_button.pack(pady=20)

        pair_play_button = tk.Button(
            start_menu_window,
            text="二人で遊ぶ（近くの人と対戦）",
            command=lambda: [
                start_menu_window.destroy(),
                self.set_mode(2),
                self.setupGUI(),
            ],
            width=28,
            font=("Helvetica", 24),
        )
        pair_play_button.pack(pady=20)

        exit_button = tk.Button(
            start_menu_window,
            text="終了する",
            command=start_menu_window.destroy,
            width=28,
            font=("Helvetica", 24),
        )
        exit_button.pack(pady=20)
        start_menu_window.mainloop()

    def set_mode(self, mode: int):
        self.mode = mode

    def show_how_to_play(self):
        how_to_play_window = tk.Tk()
        how_to_play_window.title("遊び方・ルール")
        how_to_play_window.state("zoomed")
        how_to_play_window.grab_set()

        content_frame = tk.Frame(how_to_play_window)
        content_frame.pack(fill="both", expand=True)

        text_frame = tk.Frame(content_frame)
        text_frame.pack(side="left", fill="both", expand=True, padx=10, pady=5)

        rules_text = """
        【数字集めゲームの遊び方】

        1. ゲームの目的:
            数字集めゲームは、盤面上の数字を集めてスコアを競うゲームです。
            最終的に高いスコアを持っているプレイヤーが勝利します。

        2. 基本ルール:
            ・ プレイヤーは順番に移動し、止まったマスの数字をスコアに加えます。
            ・ ターンが終了すると、もう一方のプレイヤーに交代します。
            ・ ゲームは24ターンで終了します。

        3. 特殊マス（はてなマス）:
            ・ 盤面には「?」のマスがあります。このマスに止まると、特別なイベントが発生します。
            ・ イベントにはスコアの増減や交換など、様々な効果があります。

        4. 操作方法:
            ・ プレイヤーはマスをクリックして移動します。
            ・ 移動先は上下左右のマスに限られます。

        5. モード説明:
            ・ 一人で遊ぶ（NPC対戦）:
                コンピュータ（NPC）と対戦するモードです。
                NPCの動きに合わせて、自分のスコアを高める戦略を練りましょう。
            
            ・ 二人で遊ぶ（近くの人と対戦）:
                近くの人と対戦するモードです。交互に操作して、スコアを競い合いましょう。

        6. 勝利条件:
            ・ 24ターン終了時に、スコアが高いプレイヤーが勝利します。
            ・ スコアが同じ場合は引き分けです。
        """

        rules_label = tk.Label(
            text_frame, text=rules_text, font=("Helvetica", 18), justify="left"
        )
        rules_label.pack(side="top", fill="both", expand=True)

        image_frame = tk.Frame(content_frame)
        image_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # 画像を読み込み、リサイズする
        example_image = Image.open(
            "sample.png"
        )  # ここに実際の画像ファイル名を入れてください
        example_image = example_image.resize((700, 700))
        example_photo = ImageTk.PhotoImage(example_image)

        image_label = tk.Label(image_frame, image=example_photo)
        image_label.image = example_photo
        image_label.pack(side="top", fill="both", expand=True)

        close_button = tk.Button(
            how_to_play_window,
            text="閉じる",
            command=lambda: [
                how_to_play_window.destroy(),
                self.show_start_menu_window(),
            ],
            font=("Helvetica", 24),
            width=10,
        )
        close_button.pack()

    def setupGUI(self):
        seed = random.randrange(100000)
        if self.mode == 1:
            self.palyer_name = ["プレイヤー", "NPC"]
        else:
            self.palyer_name = ["プレイヤー1", "プレイヤー2"]

        self.game = NumberCollectGame(
            seed=seed, p1_name=self.palyer_name[0], p2_name=self.palyer_name[1]
        )

        self.root = tk.Tk()
        self.root.title("数字集めゲーム")
        # self.root.geometry("900x1000")
        self.root.state("zoomed")
        self.readImage()
        self.initialize_turn_frame()
        self.initialize_score_frame()
        self.initialize_board_frame()
        self.clicked = None

        self.change_button_states_Disabled()
        self.show_first_second_spin()
        self.root.after(500, self.continue_game)
        # self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.root.mainloop()

    def show_first_second_spin(self):
        spin_window = tk.Toplevel(self.root)
        spin_window.transient(self.root)
        spin_window.grab_set()
        spin_window.protocol("WM_DELETE_WINDOW", self.close)
        spin_window.title("先攻後攻ルーレット")
        spin_window.geometry("300x200")
        spin_window.geometry(f"+0+200")
        spin_label = tk.Label(spin_window, text="", font=("Helvetica", 20))
        spin_label.pack(pady=20)
        roop = random.randrange(2, 4)
        close_button = tk.Button(
            spin_window,
            text="閉じる",
            command=spin_window.destroy,
            width=15,
            font=("Helvetica", 20),
        )
        fin = roop * 10 + self.game.player_turn
        self.spin_id = None
        f_s = [f"先攻: {self.palyer_name[0]}", f"先攻: {self.palyer_name[1]}"]

        def f(idx):
            spin_label["text"] = f_s[idx % 2]
            spin_window.update()
            self.root.update()
            if idx == fin:
                self.root.after_cancel(self.spin_id)
                close_button.pack(pady=20)
            else:
                self.spin_id = self.root.after(int(100), lambda: f(idx + 1))

        f(0)
        self.root.wait_window(spin_window)

    def close(self):
        pass

    def readImage(self):
        # 画像の読み込みとリサイズ
        red_pawn_image = Image.open("red_pawn.png").resize((80, 80))
        blue_pawn_image = Image.open("blue_pawn.png").resize((80, 80))
        none_image = Image.open("none.png").resize((150, 150))
        red_arrow_right_image = Image.open("red_arrow_r.png").resize((30, 30))
        blue_arrow_right_image = Image.open("blue_arrow_r.png").resize((30, 30))
        red_arrow_up_image = red_arrow_right_image.rotate(90, expand=True)
        red_arrow_left_image = red_arrow_right_image.rotate(180, expand=True)
        red_arrow_down_image = red_arrow_right_image.rotate(270, expand=True)
        blue_arrow_up_image = blue_arrow_right_image.rotate(90, expand=True)
        blue_arrow_left_image = blue_arrow_right_image.rotate(180, expand=True)
        blue_arrow_down_image = blue_arrow_right_image.rotate(270, expand=True)
        self.red_arrows = (
            ImageTk.PhotoImage(red_arrow_left_image),
            ImageTk.PhotoImage(red_arrow_right_image),
            ImageTk.PhotoImage(red_arrow_up_image),
            ImageTk.PhotoImage(red_arrow_down_image),
        )
        self.blue_arrows = (
            ImageTk.PhotoImage(blue_arrow_left_image),
            ImageTk.PhotoImage(blue_arrow_right_image),
            ImageTk.PhotoImage(blue_arrow_up_image),
            ImageTk.PhotoImage(blue_arrow_down_image),
        )
        self.red_pawn_photo = ImageTk.PhotoImage(red_pawn_image)
        self.blue_pawn_photo = ImageTk.PhotoImage(blue_pawn_image)
        self.none_photo = ImageTk.PhotoImage(none_image)

    def initialize_turn_frame(self):
        """ターン表示フレームを初期化する"""
        self.turn_frame = tk.Frame(self.root)
        remaining_turns_text = f"残りのターン: {END_TURN}"
        turn_text = (
            f"{self.palyer_name[0]}のターン"
            if self.game.player_turn == 0
            else f"{self.palyer_name[1]}のターン"
        )

        self.remaining_turns_label = tk.Label(
            self.turn_frame, text=remaining_turns_text, font=("Helvetica", 18)
        )
        self.turn_label = tk.Label(
            self.turn_frame, text=turn_text, font=("Helvetica", 18)
        )
        self.remaining_turns_label.pack()
        self.turn_label.pack()
        self.turn_frame.pack()

    def initialize_score_frame(self):
        """スコア表示フレームを初期化する"""
        self.score_frame = tk.Frame(self.root)
        self.player_score_label = tk.Label(
            self.score_frame,
            text=f"{self.palyer_name[0]}のスコア\n0",
            bg="#FFCCCC",
            font=("Helvetica", 18),
            width=25,
        )
        self.npc_score_label = tk.Label(
            self.score_frame,
            text=f"{self.palyer_name[1]}のスコア\n0",
            bg="#CCDDFF",
            font=("Helvetica", 18),
            width=25,
        )
        self.player_score_label.pack(side=tk.LEFT, padx=10, pady=10)
        self.npc_score_label.pack(side=tk.RIGHT, padx=10, pady=10)
        self.score_frame.pack(pady=10)

    def initialize_board_frame(self):
        """ボード表示フレームを初期化する"""
        self.board_frame = tk.Frame(self.root)
        self.board_buttons = [[None] * W for _ in range(H)]
        for i in range(H):
            for j in range(W):
                button = tk.Button(
                    self.board_frame,
                    text=self.game.points[i][j],
                    height=150,
                    width=150,
                    image=self.none_photo,
                    font=("Helvetica", 28),
                    compound="center",
                    bg="white",
                )
                button.config(command=lambda i=i, j=j: self.on_player_click(i, j))
                button.grid(row=i, column=j)
                self.board_buttons[i][j] = button
        user_x = self.game.characters[self.game.player_turn].x
        user_y = self.game.characters[self.game.player_turn].y
        npc_x = self.game.characters[self.game.player_turn ^ 1].x
        npc_y = self.game.characters[self.game.player_turn ^ 1].y

        self.board_buttons[user_x][user_y].config(
            image=self.red_pawn_photo, text="", bg="white"
        )
        self.board_buttons[npc_x][npc_y].config(
            image=self.blue_pawn_photo, text="", bg="white"
        )
        self.board_frame.pack(pady=10)

    def on_player_click(self, row, col):
        """プレイヤーがボードをクリックした時の処理"""
        for action in range(4):
            if (
                self.game.characters[0].x + dx[action] == row
                and self.game.characters[0].y + dy[action] == col
            ):
                self.clicked = action
                break
        self.change_button_states_Disabled()
        pass

    def change_button_states_Disabled(self):
        """ボード上のボタンの状態を非活性に変更する"""
        for i in range(H):
            for j in range(W):
                self.board_buttons[i][j].config(state=tk.DISABLED)

    def change_button_status_Normal(self):
        if self.mode == 2 or self.game.turn % 2 == self.game.player_turn:
            legal_acitons = self.game.legalActions()
            x = self.game.characters[0].x
            y = self.game.characters[0].y
            for action in legal_acitons:
                self.board_buttons[x + dx[action]][y + dy[action]].config(
                    state=tk.NORMAL
                )

    def continue_game(self):
        """ゲームを続行し、ゲームの終了をチェックする"""
        if self.mode == 2 or self.game.turn % 2 == self.game.player_turn:
            if self.clicked != None:
                self.change_button_states_Disabled()
                q_index = self.game.playUser(self.clicked)
                self.clicked = None
                self.move_pawn()
                self.root.update()
                if q_index != None:
                    self.show_spin(q_index)
                # print(self.game)
                self.update_display()
                self.move_pawn()
                self.root.update()
            else:
                self.change_button_status_Normal()
                self.clicked = None

        else:
            q_index = self.game.playNPC()
            self.clicked = None
            self.move_pawn()
            self.root.update()
            if q_index != None:
                self.show_spin(q_index)
            self.update_display()
            self.move_pawn()
            self.root.update()
            self.change_button_status_Normal()
            # print(self.game)

        result = self.game.checkWinigStatus()
        if result != None:
            self.root.after_cancel(self.id_)
            if result == 0:
                self.show_result(
                    f"{self.palyer_name[self.game.player_turn]}の勝利です。"
                )
            elif result == 1:
                self.show_result(
                    f"{self.palyer_name[self.game.player_turn ^ 1]}の勝利です。"
                )
            else:
                self.show_result("引き分けです。")
        else:
            if self.mode == 2 or self.game.turn % 2 == self.game.player_turn:
                self.id_ = self.root.after(100, self.continue_game)
            else:
                self.id_ = self.root.after(1000, self.continue_game)

    def show_result(self, message):
        """ゲームの結果を表示し、リトライまたは終了のオプションを提供する"""
        messagebox.showinfo("リザルト", message)
        self.show_retry_exit_options()

    def show_spin(self, tareget):
        spin_window = tk.Toplevel(self.root)
        spin_window.transient(self.root)
        spin_window.grab_set()
        spin_window.protocol("WM_DELETE_WINDOW", self.close)
        spin_window.title("はてなマスルーレット")
        spin_window.geometry("500x200")
        spin_window.geometry(f"+0+200")
        spin_label = tk.Label(spin_window, text="", font=("Helvetica", 20))
        spin_label.pack(pady=20)
        roop = random.randrange(2, 4)
        close_button = tk.Button(
            spin_window,
            text="閉じる",
            command=spin_window.destroy,
            width=10,
            font=("Helvetica", 20),
        )
        fin = roop * len(q_box) + tareget
        self.spin_id = None

        # print(fin)

        def f(idx):
            # print(idx)
            spin_label["text"] = q_str[idx % len(q_str)]
            spin_window.update()
            self.root.update()
            if idx == fin:
                self.root.after_cancel(self.spin_id)
                close_button.pack(pady=20)
            else:
                self.spin_id = self.root.after(int(100), lambda: f(idx + 1))

        f(0)
        self.root.wait_window(spin_window)

    def show_retry_exit_options(self):
        """ゲームをリトライするか終了するオプションを提供するウィンドウを作成する"""
        options_window = tk.Toplevel(self.root)
        options_window.transient(self.root)
        options_window.grab_set()
        options_window.protocol("WM_DELETE_WINDOW", self.close)
        options_window.title("メニュー")
        options_window.geometry("300x200")
        options_window.geometry(f"+0+200")

        retry_button = tk.Button(
            options_window,
            text="もう一度遊ぶ",
            command=lambda: [
                options_window.destroy(),
                self.root.destroy(),
                self.setupGUI(),
            ],
            width=15,
            font=("Helvetica", 20),
        )
        retry_button.pack(pady=20)

        exit_button = tk.Button(
            options_window,
            text="終了する",
            command=self.root.destroy,
            width=15,
            font=("Helvetica", 20),
        )
        exit_button.pack(pady=20)

    def move_pawn(self):
        for i in range(H):
            for j in range(W):
                button = self.board_buttons[i][j]
                button.config(image=self.none_photo)

        if (self.game.player_turn + self.game.turn) % 2 == 1:
            user_x = self.game.characters[1].x
            user_y = self.game.characters[1].y
            npc_x = self.game.characters[0].x
            npc_y = self.game.characters[0].y
        else:
            user_x = self.game.characters[0].x
            user_y = self.game.characters[0].y
            npc_x = self.game.characters[1].x
            npc_y = self.game.characters[1].y

        user_button = self.board_buttons[user_x][user_y]
        npc_button = self.board_buttons[npc_x][npc_y]
        user_button.config(text="", image=self.red_pawn_photo)
        npc_button.config(text="", image=self.blue_pawn_photo)

    def update_display(self):
        """ゲームの状態に基づいてGUIを更新する"""
        for i in range(H):
            for j in range(W):
                button = self.board_buttons[i][j]
                button.config(text=self.game.points[i][j], image=self.none_photo)

        self.remaining_turns_label["text"] = f"残りターン: {END_TURN - self.game.turn}"
        self.player_score_label["text"] = (
            f"{self.palyer_name[0]}のスコア\n{self.game.characters[(self.game.player_turn + self.game.turn) % 2].game_score}"
        )
        self.npc_score_label["text"] = (
            f"{self.palyer_name[1]}のスコア\n{self.game.characters[(self.game.player_turn + self.game.turn + 1) % 2].game_score}"
        )
        turn_text = (
            f"{self.palyer_name[self.game.player_turn]}のターン"
            if self.game.turn % 2 == 0
            else f"{self.palyer_name[1 ^ self.game.player_turn]}のターン"
        )
        self.turn_label["text"] = turn_text


def show_how_to_play():
    how_to_play_window = tk.Tk()
    how_to_play_window.title("遊び方・ルール")
    how_to_play_window.state("zoomed")
    how_to_play_window.grab_set()

    content_frame = tk.Frame(how_to_play_window)
    content_frame.pack(fill="both", expand=True)

    text_frame = tk.Frame(content_frame)
    text_frame.pack(side="left", fill="both", expand=True, padx=10, pady=5)

    rules_text = """
    【数字集めゲームの遊び方】

    1. ゲームの目的:
        数字集めゲームは、盤面上の数字を集めてスコアを競うゲームです。
        最終的に高いスコアを持っているプレイヤーが勝利します。

    2. 基本ルール:
        ・ プレイヤーは順番に移動し、止まったマスの数字をスコアに加えます。
        ・ ターンが終了すると、もう一方のプレイヤーに交代します。
        ・ ゲームは24ターンで終了します。

    3. 特殊マス（はてなマス）:
        ・ 盤面には「?」のマスがあります。このマスに止まると、特別なイベントが発生します。
        ・ イベントにはスコアの増減や交換など、様々な効果があります。

    4. 操作方法:
        ・ プレイヤーはマスをクリックして移動します。
        ・ 移動先は上下左右のマスに限られます。

    5. モード説明:
        ・ 一人で遊ぶ（NPC対戦）:
            コンピュータ（NPC）と対戦するモードです。
            NPCの動きに合わせて、自分のスコアを高める戦略を練りましょう。
        
        ・ 二人で遊ぶ（近くの人と対戦）:
            近くの人と対戦するモードです。交互に操作して、スコアを競い合いましょう。

    6. 勝利条件:
        ・ 24ターン終了時に、スコアが高いプレイヤーが勝利します。
        ・ スコアが同じ場合は引き分けです。
    """

    rules_label = tk.Label(
        text_frame, text=rules_text, font=("Helvetica", 18), justify="left"
    )
    rules_label.pack(side="top", fill="both", expand=True)

    image_frame = tk.Frame(content_frame)
    image_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

    # 画像を読み込み、リサイズする
    example_image = Image.open(
        "sample.png"
    )  # ここに実際の画像ファイル名を入れてください
    example_image = example_image.resize((700, 700))
    example_photo = ImageTk.PhotoImage(example_image)

    image_label = tk.Label(image_frame, image=example_photo)
    image_label.image = example_photo
    image_label.pack(side="top", fill="both", expand=True)

    close_button = tk.Button(
        how_to_play_window,
        text="閉じる",
        command=lambda: [
            how_to_play_window.destroy(),
        ],
        font=("Helvetica", 24),
        width=10,
    )
    close_button.pack()
    how_to_play_window.mainloop()


def main():
    game_GUI = NumberCollectGameGUI()
