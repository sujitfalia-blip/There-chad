# =========================================================
# ================= TEEN PATTI RULE ENGINE =================
# ================= PRODUCTION VERSION =====================
# =========================================================

from collections import Counter
from typing import List, Dict, Tuple

# =========================================================
# ================= CARD VALUES ============================
# =========================================================

CARD_VALUES = {
    "2": 2,
    "3": 3,
    "4": 4,
    "5": 5,
    "6": 6,
    "7": 7,
    "8": 8,
    "9": 9,
    "10": 10,
    "J": 11,
    "Q": 12,
    "K": 13,
    "A": 14,
}

# =========================================================
# ================= HAND PRIORITY ==========================
# =========================================================

HAND_RANKS = {
    "high_card": 1,
    "pair": 2,
    "color": 3,
    "sequence": 4,
    "pure_sequence": 5,
    "trail": 6,
}

# =========================================================
# ================= GAME CONFIG ============================
# =========================================================

BLIND_MULTIPLIER = 1
SEEN_MULTIPLIER = 2

TURN_TIME_SECONDS = 50
WARNING_TIME_SECONDS = 20

SIDE_SHOW_ALLOWED = True

# =========================================================
# ================= VALIDATE CARD ==========================
# =========================================================

def validate_cards(cards: List[str]) -> bool:

    if len(cards) != 3:
        return False

    for card in cards:

        if len(card) < 2:
            return False

        suit = card[-1]
        rank = card[:-1]

        if suit not in ["H", "D", "C", "S"]:
            return False

        if rank not in CARD_VALUES:
            return False

    return True


# =========================================================
# ================= GET CARD VALUE =========================
# =========================================================

def get_card_value(card: str) -> int:

    rank = card[:-1]

    return CARD_VALUES[rank]


# =========================================================
# ================= GET CARD SUIT ==========================
# =========================================================

def get_card_suit(card: str) -> str:

    return card[-1]


# =========================================================
# ================= SORTED VALUES ==========================
# =========================================================

def sorted_values(cards: List[str]) -> List[int]:

    values = [
        get_card_value(card)
        for card in cards
    ]

    return sorted(values)


# =========================================================
# ================= TRAIL ===============================
# =========================================================

def is_trail(cards: List[str]) -> bool:

    values = sorted_values(cards)

    return len(set(values)) == 1


# =========================================================
# ================= PAIR ==================================
# =========================================================

def is_pair(cards: List[str]) -> bool:

    values = sorted_values(cards)

    counter = Counter(values)

    return 2 in counter.values()


# =========================================================
# ================= COLOR =================================
# =========================================================

def is_color(cards: List[str]) -> bool:

    suits = [
        get_card_suit(card)
        for card in cards
    ]

    return len(set(suits)) == 1


# =========================================================
# ================= SEQUENCE ==============================
# =========================================================

def is_sequence(cards: List[str]) -> bool:

    values = sorted_values(cards)

    # NORMAL SEQUENCE

    if (
        values[0] + 1 == values[1]
        and values[1] + 1 == values[2]
    ):
        return True

    # A-2-3 SPECIAL

    if values == [2, 3, 14]:
        return True

    return False


# =========================================================
# ================= PURE SEQUENCE ==========================
# =========================================================

def is_pure_sequence(cards: List[str]) -> bool:

    return (
        is_sequence(cards)
        and is_color(cards)
    )


# =========================================================
# ================= HAND TYPE ==============================
# =========================================================

def get_hand_type(cards: List[str]) -> str:

    if not validate_cards(cards):
        raise ValueError("Invalid cards")

    if is_trail(cards):
        return "trail"

    if is_pure_sequence(cards):
        return "pure_sequence"

    if is_sequence(cards):
        return "sequence"

    if is_color(cards):
        return "color"

    if is_pair(cards):
        return "pair"

    return "high_card"


# =========================================================
# ================= HAND NAME ==============================
# =========================================================

def hand_name(cards: List[str]) -> str:

    names = {
        "trail": "Trail",
        "pure_sequence": "Pure Sequence",
        "sequence": "Sequence",
        "color": "Color",
        "pair": "Pair",
        "high_card": "High Card",
    }

    return names[get_hand_type(cards)]


# =========================================================
# ================= HAND STRENGTH ==========================
# =========================================================

def get_hand_strength(
    cards: List[str]
) -> Tuple[int, List[int]]:

    hand_type = get_hand_type(cards)

    values = sorted_values(cards)

    return (
        HAND_RANKS[hand_type],
        sorted(values, reverse=True)
    )


# =========================================================
# ================= COMPARE HANDS ==========================
# =========================================================

def compare_hands(
    cards1: List[str],
    cards2: List[str]
) -> int:

    """
    RETURNS:

    1 = Player 1 wins
    2 = Player 2 wins
    0 = Tie
    """

    strength1 = get_hand_strength(cards1)

    strength2 = get_hand_strength(cards2)

    # ================= TYPE COMPARE =================

    if strength1[0] > strength2[0]:
        return 1

    if strength2[0] > strength1[0]:
        return 2

    # ================= VALUE COMPARE =================

    for value1, value2 in zip(
        strength1[1],
        strength2[1]
    ):

        if value1 > value2:
            return 1

        if value2 > value1:
            return 2

    return 0


# =========================================================
# ================= SIDE SHOW ==============================
# =========================================================

def side_show(
    requester_cards: List[str],
    opponent_cards: List[str]
) -> bool:

    """
    RETURNS:

    True  -> requester wins
    False -> requester loses
    """

    result = compare_hands(
        requester_cards,
        opponent_cards
    )

    return result == 1


# =========================================================
# ================= BLIND CHAL =============================
# =========================================================

def calculate_chal_amount(
    current_boot: int,
    is_seen: bool
) -> int:

    if is_seen:
        return current_boot * SEEN_MULTIPLIER

    return current_boot * BLIND_MULTIPLIER


# =========================================================
# ================= TURN TIMER =============================
# =========================================================

def should_auto_pack(
    seconds_passed: int
) -> bool:

    return seconds_passed >= TURN_TIME_SECONDS


# =========================================================
# ================= ALERT TIMER ============================
# =========================================================

def should_send_alert(
    seconds_left: int
) -> bool:

    return seconds_left <= WARNING_TIME_SECONDS


# =========================================================
# ================= WINNER ================================
# =========================================================

def get_winner(
    players: List[Dict]
) -> Dict:

    """
    EXAMPLE:

    players = [
        {
            "player_id": 1,
            "cards": ["AH","AD","AS"]
        },
        {
            "player_id": 2,
            "cards": ["KH","KD","KS"]
        }
    ]
    """

    if not players:
        raise ValueError("No players found")

    winner = players[0]

    for player in players[1:]:

        result = compare_hands(
            winner["cards"],
            player["cards"]
        )

        if result == 2:
            winner = player

    return winner


# =========================================================
# ================= ADMIN MONITOR ==========================
# =========================================================

def admin_view_cards(
    players: List[Dict]
) -> List[Dict]:

    """
    ADMIN CAN SEE ALL CARDS
    """

    return players


# =========================================================
# ================= COMMISSION =============================
# =========================================================

def calculate_admin_commission(
    total_pot: float,
    percent: float = 5
) -> float:

    return round(
        (total_pot * percent) / 100,
        2
    )


# =========================================================
# ================= WINNING AMOUNT =========================
# =========================================================

def calculate_winning_amount(
    total_pot: float
) -> Dict:

    commission = calculate_admin_commission(
        total_pot
    )

    winner_amount = total_pot - commission

    return {
        "winner_amount": round(
            winner_amount,
            2
        ),
        "admin_commission": round(
            commission,
            2
        )
    }


# =========================================================
# ================= DEBUG =================================
# =========================================================

if __name__ == "__main__":

    player1 = [
        "AH",
        "AD",
        "AS"
    ]

    player2 = [
        "KH",
        "QH",
        "JH"
    ]

    print("Player 1:",
          hand_name(player1))

    print("Player 2:",
          hand_name(player2))

    print(
        "Winner:",
        compare_hands(
            player1,
            player2
        )
    )

    print(
        calculate_winning_amount(1000)
)
