import secrets

from datetime import datetime

# ================= SUITS =================

SUITS = [
    'H',   # Hearts
    'D',   # Diamonds
    'C',   # Clubs
    'S'    # Spades
]

# ================= RANKS =================

RANKS = [
    '2', '3', '4', '5',
    '6', '7', '8', '9',
    '10', 'J', 'Q', 'K', 'A'
]

# ================= FULL DECK =================

FULL_DECK = [
    f"{rank}{suit}"
    for suit in SUITS
    for rank in RANKS
]


class DeckManager:

    def __init__(self):

        # ================= GAME DATA =================

        self.deck = FULL_DECK.copy()

        self.used_cards = []

        self.dealt_cards = {}

        self.created_at = datetime.utcnow()

        self.shuffle_count = 0

        # ================= INIT =================

        self.shuffle_deck()

    # ================= SHUFFLE =================

    def shuffle_deck(self):

        """
        Secure shuffle using secrets module
        """

        shuffled = []

        temp_deck = self.deck.copy()

        while temp_deck:

            index = secrets.randbelow(
                len(temp_deck)
            )

            shuffled.append(
                temp_deck.pop(index)
            )

        self.deck = shuffled

        self.shuffle_count += 1

    # ================= DEAL CARDS =================

    def deal_cards(self, player_id):

        """
        Deal 3 unique cards
        """

        if len(self.deck) < 3:

            raise Exception(
                "Not enough cards in deck"
            )

        cards = []

        for _ in range(3):

            card = self.deck.pop(0)

            if card in self.used_cards:

                raise Exception(
                    f"Duplicate card detected: {card}"
                )

            self.used_cards.append(card)

            cards.append(card)

        self.dealt_cards[player_id] = cards

        return cards

    # ================= REMAINING =================

    def remaining_cards(self):

        return len(self.deck)

    # ================= RESET =================

    def reset_deck(self):

        self.deck = FULL_DECK.copy()

        self.used_cards = []

        self.dealt_cards = {}

        self.shuffle_deck()

    # ================= VALIDATE =================

    def validate_deck(self):

        """
        Ensure no duplicate cards exist
        """

        all_cards = self.deck + self.used_cards

        return len(all_cards) == len(
            set(all_cards)
        )

    # ================= ADMIN MONITOR =================

    def get_all_distributed_cards(self):

        """
        Admin monitoring support
        """

        return self.dealt_cards

    # ================= GAME STATE =================

    def game_state(self):

        return {

            "remaining_cards": len(self.deck),

            "used_cards": len(self.used_cards),

            "shuffle_count": self.shuffle_count,

            "is_valid": self.validate_deck()
        }

    # ================= DEBUG =================

    def print_deck(self):

        for card in self.deck:

            print(card)
