"""Remove rimborso model

Revision ID: c8602570d1de
Revises: b63e9441af68
Create Date: 2025-07-25 18:53:49.869465

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c8602570d1de'
down_revision = 'b63e9441af68'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('richieste',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('odv_id', sa.Integer(), nullable=False),
    sa.Column('evento_id', sa.Integer(), nullable=False),
    sa.Column('data_richiesta', sa.DateTime(), nullable=False),
    sa.Column('stato', sa.Enum('IN_ATTESA', 'APPROVATA', 'PARZIALMENTE_APPROVATA', 'RIFIUTATA', name='statorichiesta'), nullable=False),
    sa.Column('note_richiedente', sa.Text(), nullable=True),
    sa.Column('note_istruttore', sa.Text(), nullable=True),
    sa.Column('approvato_da', sa.Integer(), nullable=True),
    sa.Column('data_approvazione', sa.DateTime(), nullable=True),
    sa.Column('data_creazione', sa.DateTime(), nullable=True),
    sa.Column('data_modifica', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['approvato_da'], ['user.id'], ),
    sa.ForeignKeyConstraint(['evento_id'], ['eventi.id'], ),
    sa.ForeignKeyConstraint(['odv_id'], ['odv.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('impiego_mezzo',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('mezzo_id', sa.Integer(), nullable=False),
    sa.Column('evento_id', sa.Integer(), nullable=False),
    sa.Column('data_inizio', sa.DateTime(), nullable=False),
    sa.Column('data_fine', sa.DateTime(), nullable=False),
    sa.Column('km_partenza', sa.Integer(), nullable=False),
    sa.Column('km_arrivo', sa.Integer(), nullable=False),
    sa.Column('note', sa.Text(), nullable=True),
    sa.Column('data_creazione', sa.DateTime(), nullable=True),
    sa.Column('data_modifica', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['evento_id'], ['eventi.id'], ),
    sa.ForeignKeyConstraint(['mezzo_id'], ['mezzo.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('spese',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('richiesta_id', sa.Integer(), nullable=False),
    sa.Column('tipo', sa.Enum('CARBURANTE', 'VITTO', 'PEDAGGI', 'RIPRISTINO', 'PARCHEGGIO', 'ALTRO', name='tipospesa'), nullable=False),
    sa.Column('data_spesa', sa.Date(), nullable=False),
    sa.Column('importo_richiesto', sa.Float(), nullable=False),
    sa.Column('importo_approvato', sa.Float(), nullable=True),
    sa.Column('note', sa.Text(), nullable=True),
    sa.Column('data_creazione', sa.DateTime(), nullable=True),
    sa.Column('data_modifica', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['richiesta_id'], ['richieste.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('giustificativi',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('spesa_id', sa.Integer(), nullable=False),
    sa.Column('tipo', sa.Enum('FATTURA', 'SCONTRINO', 'RICEVUTA', 'ALTRO', name='tipogiustificativo'), nullable=False),
    sa.Column('numero', sa.String(length=100), nullable=True),
    sa.Column('data_emissione', sa.Date(), nullable=False),
    sa.Column('emesso_da', sa.String(length=255), nullable=False),
    sa.Column('importo', sa.Float(), nullable=False),
    sa.Column('file_path', sa.String(length=255), nullable=False),
    sa.Column('data_creazione', sa.DateTime(), nullable=True),
    sa.Column('data_modifica', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['spesa_id'], ['spese.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('spese_altro',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('descrizione_dettagliata', sa.Text(), nullable=False),
    sa.ForeignKeyConstraint(['id'], ['spese.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('spese_carburante',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('impiego_mezzo_id', sa.Integer(), nullable=False),
    sa.Column('tipo_carburante', sa.String(length=50), nullable=False),
    sa.Column('litri', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['id'], ['spese.id'], ),
    sa.ForeignKeyConstraint(['impiego_mezzo_id'], ['impiego_mezzo.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('spese_parcheggio',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('indirizzo', sa.String(length=255), nullable=True),
    sa.Column('durata_ore', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['id'], ['spese.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('spese_pedaggi',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('impiego_mezzo_id', sa.Integer(), nullable=False),
    sa.Column('tratta', sa.String(length=255), nullable=False),
    sa.ForeignKeyConstraint(['id'], ['spese.id'], ),
    sa.ForeignKeyConstraint(['impiego_mezzo_id'], ['impiego_mezzo.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('spese_ripristino',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('impiego_mezzo_id', sa.Integer(), nullable=False),
    sa.Column('descrizione_intervento', sa.Text(), nullable=False),
    sa.ForeignKeyConstraint(['id'], ['spese.id'], ),
    sa.ForeignKeyConstraint(['impiego_mezzo_id'], ['impiego_mezzo.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('spese_vitto',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('numero_pasti', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['id'], ['spese.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('rimborso')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('rimborso',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('data_richiesta', sa.DATETIME(), nullable=True),
    sa.Column('descrizione', sa.VARCHAR(length=200), nullable=False),
    sa.Column('importo', sa.FLOAT(), nullable=False),
    sa.Column('data_spesa', sa.DATE(), nullable=False),
    sa.Column('categoria', sa.VARCHAR(length=50), nullable=True),
    sa.Column('stato', sa.VARCHAR(length=20), nullable=True),
    sa.Column('note', sa.TEXT(), nullable=True),
    sa.Column('file_allegato', sa.VARCHAR(length=200), nullable=True),
    sa.Column('user_id', sa.INTEGER(), nullable=False),
    sa.Column('approvato_da', sa.INTEGER(), nullable=True),
    sa.Column('data_approvazione', sa.DATETIME(), nullable=True),
    sa.ForeignKeyConstraint(['approvato_da'], ['user.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('spese_vitto')
    op.drop_table('spese_ripristino')
    op.drop_table('spese_pedaggi')
    op.drop_table('spese_parcheggio')
    op.drop_table('spese_carburante')
    op.drop_table('spese_altro')
    op.drop_table('giustificativi')
    op.drop_table('spese')
    op.drop_table('impiego_mezzo')
    op.drop_table('richieste')
    # ### end Alembic commands ###
