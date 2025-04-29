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

# Classes do ORM
class Estado(Base):
    __tablename__ = 'Estado'
    
    uf = Column(String, primary_key=True)
    nome = Column(String)
    
    municipios = relationship("Municipio", back_populates="estado")

class Municipio(Base):
    __tablename__ = 'Municipio'
    
    idMunicipio = Column(String, primary_key=True)
    uf = Column(String, ForeignKey('Estado.uf'))
    nome = Column(String)
    idTipoCapital = Column(Integer, ForeignKey('TipoCapital.idTipoCapital'))
    
    estado = relationship("Estado", back_populates="municipios")
    escolas = relationship("Escola", back_populates="municipio")
    tipos_capital = relationship("TipoCapital", back_populates="municipio")

class TipoCapital(Base):
    __tablename__ = 'TipoCapital'
    
    idTipoCapital = Column(Integer, primary_key=True)
    nome = Column(String)
    
    municipio = relationship("Municipio", back_populates="tipos_capital")

class Escola(Base):
    __tablename__ = 'Escola'
    
    idEscola = Column(String, primary_key=True)
    idMunicipio = Column(String, ForeignKey('Municipio.idMunicipio'))
    nome = Column(String)
    
    municipio = relationship("Municipio", back_populates="escolas")
    indicadores_alunos = relationship("IndicadoresAlunos", back_populates="escola")
    notas_ideb = relationship("NotaIDEB", back_populates="escola")
    notas_saeb = relationship("NotaSAEB", back_populates="escola")
    taxas_aprovacao = relationship("TaxasAprovacao", back_populates="escola")

class NivelEscolaridade(Base):
    __tablename__ = 'NivelEscolariade'
    
    idEscolaridadePais = Column(Integer, primary_key=True)
    escolaridade = Column(String)
    
    classificacoes_se = relationship("ClassificacaoSocioEconomica", back_populates="escolaridade_pais")

class ClassificacaoSocioEconomica(Base):
    __tablename__ = 'ClassificacaoSocioEconomica'
    
    idClassificacaoSE = Column(Integer, primary_key=True)
    qtdQuartos = Column(Integer)
    qtdCelulares = Column(Integer)
    qtdGeladeiras = Column(Integer)
    qtdTelevisores = Column(Integer)
    qtdBanheiros = Column(Integer)
    idEscolaridadePais = Column(Integer, ForeignKey('NivelEscolariade.idEscolaridadePais'))
    qtdComputadores = Column(Integer)
    qtdCarros = Column(Integer)
    
    escolaridade_pais = relationship("NivelEscolaridade", back_populates="classificacoes_se")
    porcentagens_alunos = relationship("PorcentagemClassificacaoAlunos", back_populates="classificacao_se")

class IndicadoresAlunos(Base):
    __tablename__ = 'IndicadoresAlunos'
    
    idIndicadoresAlunos = Column(Integer, primary_key=True, autoincrement=True)
    qtdAlunosInse = Column(Integer)
    anoMedicao = Column(Integer)
    idEscola = Column(String, ForeignKey('Escola.idEscola'))
    
    escola = relationship("Escola", back_populates="indicadores_alunos")
    porcentagens_classificacao = relationship("PorcentagemClassificacaoAlunos", back_populates="indicadores_alunos")

class PorcentagemClassificacaoAlunos(Base):
    __tablename__ = 'PorcentagemClassificacaoAlunos'
    
    idPorcentagem = Column(Integer, primary_key=True, autoincrement=True)
    idIndicadoresAlunos = Column(Integer, ForeignKey('IndicadoresAlunos.idIndicadoresAlunos'))
    idClassificacaoSE = Column(Integer, ForeignKey('ClassificacaoSocioEconomica.idClassificacaoSE'))
    porcentagemAlunos = Column(Double)
    
    indicadores_alunos = relationship("IndicadoresAlunos", back_populates="porcentagens_classificacao")
    classificacao_se = relationship("ClassificacaoSocioEconomica", back_populates="porcentagens_alunos")

class NotaIDEB(Base):
    __tablename__ = 'NotaIDEB'
    
    idIdeb = Column(Integer, primary_key=True, autoincrement=True)
    idEscola = Column(String, ForeignKey('Escola.idEscola'))
    notaIdeb = Column(Double)
    anoMedicao = Column(Integer)
    
    escola = relationship("Escola", back_populates="notas_ideb")

class NotaSAEB(Base):
    __tablename__ = 'NotaSAEB'
    
    idSaeb = Column(Integer, primary_key=True, autoincrement=True)
    idEscola = Column(String, ForeignKey('Escola.idEscola'))
    notaMatematica = Column(Double)
    notaLinguaPort = Column(Double)
    notaPadronizada = Column(Double)
    anoMedicao = Column(Integer)
    
    escola = relationship("Escola", back_populates="notas_saeb")

class TaxasAprovacao(Base):
    __tablename__ = 'TaxasAprovacao'
    
    idTaxasAprovacao = Column(Integer, primary_key=True, autoincrement=True)
    idEscola = Column(String, ForeignKey('Escola.idEscola'))
    anoMedicao = Column(Integer)
    total = Column(Double)
    
    escola = relationship("Escola", back_populates="taxas_aprovacao")
    aprovacoes_series = relationship("AprovacaoSerie", back_populates="taxas_aprovacao")

class AprovacaoSerie(Base):
    __tablename__ = 'AprovacaoSerie'
    
    idAprovacaoSerie = Column(Integer, primary_key=True, autoincrement=True)
    serie = Column(Integer)
    porcentagem = Column(Double)
    idTaxasAprovacao = Column(Integer, ForeignKey('TaxasAprovacao.idTaxasAprovacao'))
    
    taxas_aprovacao = relationship("TaxasAprovacao", back_populates="aprovacoes_series")


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

def incluir_tipos_capital():
    for id, nome in tipos_capital.keys():
        tipoCapital = TipoCapital(idTipoCapital=id, nome=nome)
        session.add(tipoCapital)

def incluir_niveis_escolaridade():
    for id_nivel, descricao in niveis_escolaridade.items():
        nivel = NivelEscolaridade(idEscolaridadePais=id_nivel, escolaridade=descricao)
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

def processar_estados_municipios(df):
    incluir_tipos_capital()

    # Processar estados
    for uf, name in UF_TO_STATE_NAME.keys():
        estado = Estado(uf=uf, nome=name)
        session.add(estado)
    
    # Processar Municipios
    municipios = df[['CO_MUNICIPIO', 'SG_UF', 'NO_MUNICIPIO', 'TP_CAPITAL']].drop_duplicates()
    for _, row in municipios.iterrows():
        municipio = Municipio(
            idMunicipio=str(row['CO_MUNICIPIO']),
            uf=row['SG_UF'],
            nome=row['NO_MUNICIPIO'],
            idTipoCapital=row['TP_CAPITAL']
        )
        session.add(municipio)

def processar_escolas(df):
    escolas = df[['ID_ESCOLA', 'CO_MUNICIPIO', 'NO_ESCOLA', 'TP_CAPITAL']].drop_duplicates()
    for _, row in escolas.iterrows():
        escola = Escola(
            idEscola=str(row['ID_ESCOLA']),
            idMunicipio=str(row['CO_MUNICIPIO']),
            nome=row['NO_ESCOLA'],
        )
        session.add(escola)

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