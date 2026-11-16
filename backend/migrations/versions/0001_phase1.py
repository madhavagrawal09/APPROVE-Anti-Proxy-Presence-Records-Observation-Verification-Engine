"""Initial APPROVE Phase 1 schema."""
from alembic import op
from app.db import Base
import app.db
revision="0001_phase1"
down_revision=None
branch_labels=None
depends_on=None
def upgrade(): Base.metadata.create_all(bind=op.get_bind())
def downgrade(): Base.metadata.drop_all(bind=op.get_bind())
