"""Add missing features

Revision ID: add_missing_features
Revises: c54814ee04e7
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_missing_features'
down_revision = 'c54814ee04e7'
branch_labels = None
depends_on = None

def upgrade():
    # Ajouter les colonnes de validation aux notes
    op.add_column('notes', sa.Column('validee', sa.Boolean(), nullable=True, default=False))
    op.add_column('notes', sa.Column('validee_par', sa.Integer(), nullable=True))
    op.add_column('notes', sa.Column('date_validation', sa.DateTime(), nullable=True))
    op.add_column('notes', sa.Column('commentaire_validation', sa.Text(), nullable=True))
    
    # Créer la table des messages
    op.create_table('messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('expediteur_id', sa.Integer(), nullable=False),
        sa.Column('destinataire_id', sa.Integer(), nullable=False),
        sa.Column('sujet', sa.String(length=200), nullable=False),
        sa.Column('contenu', sa.Text(), nullable=False),
        sa.Column('lu', sa.Boolean(), nullable=True, default=False),
        sa.Column('date_envoi', sa.DateTime(), nullable=True),
        sa.Column('date_lecture', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['destinataire_id'], ['utilisateurs.id'], ),
        sa.ForeignKeyConstraint(['expediteur_id'], ['utilisateurs.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Créer la table des frais de scolarité
    op.create_table('frais_scolarite',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('etudiant_id', sa.Integer(), nullable=False),
        sa.Column('annee_academique_id', sa.Integer(), nullable=False),
        sa.Column('montant_total', sa.Float(), nullable=False),
        sa.Column('montant_paye', sa.Float(), nullable=True, default=0),
        sa.Column('date_limite', sa.Date(), nullable=True),
        sa.Column('statut', sa.String(length=20), nullable=True, default='impaye'),
        sa.Column('date_creation', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['annee_academique_id'], ['annees_academiques.id'], ),
        sa.ForeignKeyConstraint(['etudiant_id'], ['etudiants.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Créer la table des paiements
    op.create_table('paiements',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('frais_id', sa.Integer(), nullable=False),
        sa.Column('montant', sa.Float(), nullable=False),
        sa.Column('mode_paiement', sa.String(length=50), nullable=False),
        sa.Column('reference', sa.String(length=100), nullable=True),
        sa.Column('date_paiement', sa.DateTime(), nullable=True),
        sa.Column('enregistre_par', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['enregistre_par'], ['utilisateurs.id'], ),
        sa.ForeignKeyConstraint(['frais_id'], ['frais_scolarite.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    # Supprimer les colonnes de validation des notes
    op.drop_column('notes', 'commentaire_validation')
    op.drop_column('notes', 'date_validation')
    op.drop_column('notes', 'validee_par')
    op.drop_column('notes', 'validee')
    
    # Supprimer les tables
    op.drop_table('paiements')
    op.drop_table('frais_scolarite')
    op.drop_table('messages') 