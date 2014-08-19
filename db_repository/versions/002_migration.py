from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
cost_center = Table('cost_center', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('name', String),
    Column('cc_ref', String),
    Column('gl', Integer),
    Column('fn_text', String),
    Column('co_code', String),
    Column('trd_partner', String),
)

profit_center = Table('profit_center', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('name', String),
    Column('pc_ref', String),
    Column('gl', Integer),
    Column('fn_text', String),
    Column('co_code', String),
    Column('tax', String),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['cost_center'].create()
    post_meta.tables['profit_center'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['cost_center'].drop()
    post_meta.tables['profit_center'].drop()
