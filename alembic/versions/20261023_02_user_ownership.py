"""Add user ownership and RLS policies."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
revision="20261023_02";down_revision="20261023_01";branch_labels=None;depends_on=None
def upgrade():
    op.add_column("plans",sa.Column("owner_id",postgresql.UUID(as_uuid=True),nullable=True));op.create_index("ix_plans_owner_id","plans",["owner_id"])
    op.add_column("bucket_list_items",sa.Column("owner_id",postgresql.UUID(as_uuid=True),nullable=True));op.create_index("ix_bucket_list_items_owner_id","bucket_list_items",["owner_id"])
    op.execute("ALTER TABLE plans ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE bucket_list_items ENABLE ROW LEVEL SECURITY")
    op.execute("CREATE POLICY plans_owner_policy ON plans FOR ALL TO authenticated USING (owner_id = auth.uid()) WITH CHECK (owner_id = auth.uid())")
    op.execute("CREATE POLICY bucket_owner_policy ON bucket_list_items FOR ALL TO authenticated USING (owner_id = auth.uid()) WITH CHECK (owner_id = auth.uid())")
def downgrade():
    op.execute("DROP POLICY IF EXISTS bucket_owner_policy ON bucket_list_items");op.execute("DROP POLICY IF EXISTS plans_owner_policy ON plans")
    op.drop_index("ix_bucket_list_items_owner_id",table_name="bucket_list_items");op.drop_column("bucket_list_items","owner_id")
    op.drop_index("ix_plans_owner_id",table_name="plans");op.drop_column("plans","owner_id")
