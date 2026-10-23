"""Add editable task estimates and persisted timer state."""
from alembic import op
import sqlalchemy as sa
revision="20261023_04";down_revision="20261023_03";branch_labels=None;depends_on=None
def upgrade():
    op.add_column("tasks",sa.Column("status",sa.String(30),nullable=False,server_default="Pending"))
    op.add_column("tasks",sa.Column("estimated_minutes",sa.Integer(),nullable=False,server_default="30"))
    op.add_column("tasks",sa.Column("accumulated_seconds",sa.Integer(),nullable=False,server_default="0"))
    op.add_column("tasks",sa.Column("started_at",sa.DateTime(timezone=True),nullable=True))
    op.execute("UPDATE tasks SET status = CASE WHEN completed THEN 'Completed' ELSE 'Pending' END")
def downgrade():
    op.drop_column("tasks","started_at");op.drop_column("tasks","accumulated_seconds");op.drop_column("tasks","estimated_minutes");op.drop_column("tasks","status")
