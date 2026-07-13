"""ORM models. Importing this package registers every table on Base.metadata
(used by Alembic's autogenerate and by the app at runtime)."""

from app.models.dream import Dream
from app.models.dream_embedding import DreamEmbedding
from app.models.dream_emotion import DreamEmotion
from app.models.dream_symbol import DreamSymbol
from app.models.emotion import Emotion
from app.models.interpretation import Interpretation
from app.models.pattern import Pattern
from app.models.profile import Profile
from app.models.share_card import ShareCard
from app.models.streak import Streak
from app.models.subscription import Subscription
from app.models.symbol import Symbol
from app.models.usage_quota import UsageQuota
from app.models.user import User

__all__ = [
    "Dream",
    "DreamEmbedding",
    "DreamEmotion",
    "DreamSymbol",
    "Emotion",
    "Interpretation",
    "Pattern",
    "Profile",
    "ShareCard",
    "Streak",
    "Subscription",
    "Symbol",
    "UsageQuota",
    "User",
]
