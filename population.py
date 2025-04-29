import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, Double, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from constants import *
from psycopg2 import *

from secrets_db import *

DESEMPENHO_ESCOLAR_CSV = 'datasets/desempenho_escolar.csv'
INDICADORES_SOCIO_ECONOMICOS_CSV = 'datasets/indicadores_socio_economicos.csv'

# Criar engine do SQLAlchemy
DATABASE_URL = f'postgresql://{USERNAME}:{PASSWORD}@{HOST}/{BASE_NAME}'
engine = create_engine(DATABASE_URL)
Base = declarative_base()

# Definir modelos SQLAlchemy
class Estado(Base):
    _tablename_ = 'Estado'
    uf = Column(String, primary_key=True)
    nome = Column(String)
    municipios = relationship("Municipio", back_populates="estado")

class Municipio(Base):
    _tablename_ = 'Município'
    idMunicipio = Column(String, primary_key=True)
    uf = Column(String, ForeignKey('Estado.uf'))
    nome = Column(String)
    tipoCapital = Column(String)
    estado = relationship("Estado", back_populates="municipios")
    escolas = relationship("Escola", back_populates="municipio")

class Escola(Base):
    _tablename_ = 'Escola'
    idEscola = Column(String, primary_key=True)
    idMunicipio = Column(String, ForeignKey('Município.idMunicipio'))
    nome = Column(String)
    tipoCapital = Column(String)
    municipio = relationship("Municipio", back_populates="escolas")
    indicadores = relationship("IndicadoresAlunos", back_populates="escola")
    taxas_aprovacao = relationship("TaxasAprovacao", back_populates="escola")
    notas_ideb = relationship("NotaIDEB", back_populates="escola")
    notas_saeb = relationship("NotaSAEB", back_populates="escola")

class IndicadoresAlunos(Base):
    _tablename_ = 'IndicadoresAlunos'
    idIndicadoresAlunos = Column(Integer, primary_key=True)
    qtdAlunosInse = Column(Integer)
    anoMedicao = Column(Integer)
    idEscola = Column(String, ForeignKey('Escola.idEscola'))
    escola = relationship("Escola", back_populates="indicadores")
    porcentagens = relationship("PorcentagemClassificacaoAlunos", back_populates="indicador")

class ClassificacaoSocioEconomica(Base):
    _tablename_ = 'ClassificacaoSocioEconomica'
    idClassificacaoSE = Column(Integer, primary_key=True)
    qtdQuartos = Column(Integer)
    qtdCelulares = Column(Integer)
    qtdGeladeiras = Column(Integer)
    qtdTelevisores = Column(Integer)
    qtdBanheiros = Column(Integer)
    idEscolaridadePais = Column(Integer, ForeignKey('NivelEscolariade.idEscolaridadePais'))
    escolaridade_pais = relationship("NivelEscolariade", back_populates="classificacoes")
    porcentagens = relationship("PorcentagemClassificacaoAlunos", back_populates="classificacao")

class NivelEscolariade(Base):
    _tablename_ = 'NivelEscolariade'
    idEscolaridadePais = Column(Integer, primary_key=True)
    escolaridade = Column(String)
    classificacoes = relationship("ClassificacaoSocioEconomica", back_populates="escolaridade_pais")

class PorcentagemClassificacaoAlunos(Base):
    _tablename_ = 'PorcentagemClassificacaoAlunos'
    idPorcentagem = Column(Integer, primary_key=True)
    idIndicadoresAlunos = Column(Integer, ForeignKey('IndicadoresAlunos.idIndicadoresAlunos'))
    idClassificacaoSE = Column(Integer, ForeignKey('ClassificacaoSocioEconomica.idClassificacaoSE'))
    porcentagemAlunos = Column(Double)
    indicador = relationship("IndicadoresAlunos", back_populates="porcentagens")
    classificacao = relationship("ClassificacaoSocioEconomica", back_populates="porcentagens")

class TaxasAprovacao(Base):
    _tablename_ = 'TaxasAprovacao'
    idTaxasAprovacao = Column(Integer, primary_key=True)
    idEscola = Column(String, ForeignKey('Escola.idEscola'))
    anoMedicao = Column(Integer)
    total = Column(Double)
    escola = relationship("Escola", back_populates="taxas_aprovacao")
    aprovacoes_serie = relationship("AprovacaoSerie", back_populates="taxa_aprovacao")

class NotaIDEB(Base):
    _tablename_ = 'NotaIDEB'
    idIdeb = Column(Integer, primary_key=True)
    idEscola = Column(String, ForeignKey('Escola.idEscola'))
    notaIdeb = Column(Double)
    anoMedicao = Column(Integer)
    escola = relationship("Escola", back_populates="notas_ideb")

class NotaSAEB(Base):
    _tablename_ = 'NotaSAEB'
    idSaeb = Column(Integer, primary_key=True)
    idEscola = Column(String, ForeignKey('Escola.idEscola'))
    notaMatematica = Column(Double)
    notaLinguaPort = Column(Double)
    notaPadronizada = Column(Double)
    anoMedicao = Column(Integer)
    escola = relationship("Escola", back_populates="notas_saeb")

class AprovacaoSerie(Base):
    _tablename_ = 'AprovacaoSerie'
    idAprovacaoSerie = Column(Integer, primary_key=True)
    serie = Column(Integer)
    porcentagem = Column(Double)
    idTaxasAprovacao = Column(Integer, ForeignKey('TaxasAprovacao.idTaxasAprovacao'))
    taxa_aprovacao = relationship("TaxasAprovacao", back_populates="aprovacoes_serie")


# Criar todas as tabelas no banco de dados
Base.metadata.create_all(engine)

# Criar sessão
Session = sessionmaker(bind=engine)
session = Session()

def carregar_dados():
    # Carregar dados das planilhas
    df_indicadores_se = pd.read_excel(INDICADORES_SOCIO_ECONOMICOS_CSV)
    df_desempenho_escolar = pd.read_excel(DESEMPENHO_ESCOLAR_CSV, decimal=",")
    
    # Processar dados e popular o banco
    processar_estados_municipios(df_indicadores_se)
    processar_escolas(df_indicadores_se)
    processar_indicadores(df_indicadores_se)
    processar_taxas_aprovacao(df_desempenho_escolar)
    processar_notas(df_desempenho_escolar)
    
    session.commit()
    session.close()

def processar_estados_municipios(df):
    # Processar estados
    for uf, name in UF_TO_STATE_NAME.keys():
        estado = Estado(uf=uf, nome=name)
        session.add(estado)
    
    # Processar municípios
    municipios = df[['CO_MUNICIPIO', 'SG_UF', 'NO_MUNICIPIO', 'TP_CAPITAL']].drop_duplicates()
    for _, row in municipios.iterrows():
        municipio = Municipio(
            idMunicipio=str(row['CO_MUNICIPIO']),
            uf=row['SG_UF'],
            nome=row['NO_MUNICIPIO'],
            tipoCapital=row['TP_CAPITAL']
        )
        session.add(municipio)

def processar_escolas(df):
    escolas = df[['ID_ESCOLA', 'CO_MUNICIPIO', 'NO_ESCOLA', 'TP_CAPITAL']].drop_duplicates()
    for _, row in escolas.iterrows():
        escola = Escola(
            idEscola=str(row['ID_ESCOLA']),
            idMunicipio=str(row['CO_MUNICIPIO']),
            nome=row['NO_ESCOLA'],
            tipoCapital=row['TP_CAPITAL']
        )
        session.add(escola)

def incluir_niveis_escolaridade():
    for id_nivel, descricao in niveis_escolaridade.items():
        nivel = NivelEscolariade(idEscolaridadePais=id_nivel, escolaridade=descricao)
        session.add(nivel)


def incluir_classificacoes_socio_economicas():
    for num_nivel, informacoes in niveis_socio_economicos.items():
        nivelSE = ClassificacaoSocioEconomica(
            idClassificacaoSE=num_nivel, 
            qtdGeladeiras=informacoes['qtdGeladeiras'], 
            qtdTelevisores=informacoes['qtdTelevisores'], 
            qtdBanheiros=informacoes['qtdBanheiros'], 
            qtdCelulares=informacoes['qtdCelulares'], 
            qtdQuartos=informacoes['qtdQuartos'], 
            qtdCarros=informacoes['qtdCarros'], 
            qtdComputadores=informacoes['qtdComputadores'], 
            idEscolaridadePais=informacoes['idEscolaridadePais']
        )
        session.add(nivelSE)

def processar_indicadores(df):
    incluir_niveis_escolaridade()
    incluir_classificacoes_socio_economicas()
    
    # Processar indicadores de alunos
    for _, row in df.iterrows():
        indicador = IndicadoresAlunos(
            # idIndicadoresAlunos=int(row['ID_ESCOLA'] + str(row['NU_ANO_SAEB'])), TODO: auto incrementado
            qtdAlunosInse=row['QTD_ALUNOS_INSE'],
            anoMedicao=row['NU_ANO_SAEB'],
            idEscola=str(row['ID_ESCOLA'])
        )
        session.add(indicador)
        session.flush()
        
        # Processar porcentagens de classificação
        for nivel in range(1, 9):
            porcentagem = row[f'PC_NIVEL_{nivel}']
            porc_class = PorcentagemClassificacaoAlunos(
                # idPorcentagem=int(f"{row['ID_ESCOLA']}{row['NU_ANO_SAEB']}{nivel}"),
                idIndicadoresAlunos=indicador.idIndicadoresAlunos,
                idClassificacaoSE=nivel,
                porcentagemAlunos=porcentagem
            )
            session.add(porc_class)

def processar_taxas_aprovacao(df):
    # Esta função é um exemplo - ajuste conforme os dados reais da planilha Divulgacao EM
    for _, row in df.iterrows():
        for ano in [2017, 2019, 2021, 2023]:
            taxa = TaxasAprovacao(
                idEscola=str(row['ID_ESCOLA']),
                anoMedicao=ano,
                total=row[f'VL_APROVACAO_{ano}_SI_4']  # Substitua pelo valor real se disponível
            )
            session.add(taxa)
            session.flush()
            
            # Exemplo para séries (ajuste conforme necessário)
            for serie in range(1, 5):
                aprovacao = AprovacaoSerie(
                    serie=serie,
                    porcentagem=row[f'VL_APROVACAO_{ano}_{serie}'],  # Substitua pelo valor real
                    idTaxasAprovacao=taxa.idTaxasAprovacao
                )
                session.add(aprovacao)

def processar_notas(df):
    for _, row in df.iterrows():
        for ano in [2017, 2019, 2021, 2023]:
            # Notas IDEB (ajuste conforme os dados reais)
            ideb = NotaIDEB(
                idEscola=str(row['ID_ESCOLA']),
                notaIdeb=row[f'VL_OBSERVADO_{ano}'],  # Substitua pelo valor real
                anoMedicao=row['NU_ANO_SAEB']
            )
            session.add(ideb)
            
            # Notas SAEB (ajuste conforme os dados reais)
            saeb = NotaSAEB(
                idEscola=str(row['ID_ESCOLA']),
                notaMatematica=row[f'VL_NOTA_MATEMATICA_{ano}'],  # Substitua pelo valor real
                notaLinguaPort=row[f'VL_NOTA_PORTUGUES_{ano}'],  # Substitua pelo valor real
                notaPadronizada=row[f'VL_NOTA_MEDIA_{ano}'],  # Substitua pelo valor real
                anoMedicao=row['NU_ANO_SAEB']
            )
            session.add(saeb)

if __name__ == '':
    carregar_dados()
    print("Dados carregados com sucesso!")