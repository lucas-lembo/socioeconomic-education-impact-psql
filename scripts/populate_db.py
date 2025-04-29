import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, Double, ForeignKey, MetaData, text
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
    __tablename__ = 'NivelEscolaridade'
    
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
    idEscolaridadePais = Column(Integer, ForeignKey('NivelEscolaridade.idEscolaridadePais'))
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
    df_indicadores_se = pd.read_csv(INDICADORES_SOCIO_ECONOMICOS_CSV)
    df_desempenho_escolar = pd.read_csv(DESEMPENHO_ESCOLAR_CSV)
    
    # Processar dados e popular o banco
    processar_estados_municipios(df_indicadores_se)
    processar_escolas(df_indicadores_se)
    processar_indicadores(df_indicadores_se)
    processar_taxas_aprovacao(df_desempenho_escolar)
    processar_notas(df_desempenho_escolar)
    
    session.commit()
    session.close()

def incluir_tipos_capital():
    for id, nome in tipos_capital.items():
        tipoCapital = TipoCapital(idTipoCapital=id, nome=nome)
        session.add(tipoCapital)
    print('TipoCapital inseridos!')

def incluir_niveis_escolaridade():
    for id_nivel, descricao in niveis_escolaridade.items():
        nivel = NivelEscolaridade(idEscolaridadePais=id_nivel, escolaridade=descricao)
        session.add(nivel)
    print('Nivel Escolaridade inseridos!')


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
    print('ClassificacoesSE inseridos!')


def incluir_estados():
    # Processar estados
    for uf, name in UF_TO_STATE_NAME.items():
        estado = Estado(uf=uf, nome=name)
        session.add(estado)
    print('Estados inseridos!')

def processar_estados_municipios(df):
    incluir_tipos_capital()
    incluir_estados()
    
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
    
    print('Municipios inseridos!')


def processar_escolas(df):
    escolas = df[['ID_ESCOLA', 'CO_MUNICIPIO', 'NO_ESCOLA', 'TP_CAPITAL']].drop_duplicates()
    counter = 0
    for _, row in escolas.iterrows():
        escola = Escola(
            idEscola=str(row['ID_ESCOLA']),
            idMunicipio=str(row['CO_MUNICIPIO']),
            nome=row['NO_ESCOLA'],
        )
        session.add(escola)
        print(f'{counter}: Escola {escola.nome} inserida!')
        counter+=1

    print('Escolas inseridos!')

def processar_indicadores(df):
    incluir_niveis_escolaridade()
    incluir_classificacoes_socio_economicas()
    
    # Processar indicadores de alunos
    counter=0
    for _, row in df.iterrows():
        indicador = IndicadoresAlunos(
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
                idIndicadoresAlunos=indicador.idIndicadoresAlunos,
                idClassificacaoSE=nivel,
                porcentagemAlunos=porcentagem
            )
            session.add(porc_class)

        print(f'{counter}: Indicadores da escola de ID {indicador.idEscola} inseridos!')
        counter += 1

    print('Indicadores inseridos!')


def processar_taxas_aprovacao(df):
    # Esta função é um exemplo - ajuste conforme os dados reais da planilha Divulgacao EM
    counter = 0
    for _, row in df.iterrows():
        for ano in [2017, 2019, 2021, 2023]:
            total = row[f'VL_APROVACAO_{ano}_SI_4']
            total = total if total not in ['-', 'ND', 'ND***'] else None
            taxa = TaxasAprovacao(
                idEscola=str(row['ID_ESCOLA']),
                anoMedicao=ano,
                total=total  # Substitua pelo valor real se disponível
            )
            session.add(taxa)
            session.flush()
            
            # Exemplo para séries (ajuste conforme necessário)
            for serie in range(1, 5):
                porcentagem = row[f'VL_APROVACAO_{ano}_{serie}']
                porcentagem = porcentagem if porcentagem not in ['-', 'ND', 'ND***'] else None
                aprovacao = AprovacaoSerie(
                    serie=serie,
                    porcentagem=porcentagem,  # Substitua pelo valor real
                    idTaxasAprovacao=taxa.idTaxasAprovacao
                )
                session.add(aprovacao)
        print(f'{counter}: Taxa aprovacao {taxa.escola.nome} inserida!')
        counter += 1

    print('TaxasAprovacao inseridos!')

def processar_notas(df):
    counter = 0
    for _, row in df.iterrows():
        for ano in [2017, 2019, 2021, 2023]:
            notaIdeb = row[f'VL_OBSERVADO_{ano}']
            notaIdeb = notaIdeb if notaIdeb not in ['-', 'ND', 'ND***'] else None
            # Notas IDEB (ajuste conforme os dados reais)
            ideb = NotaIDEB(
                idEscola=str(row['ID_ESCOLA']),
                notaIdeb=notaIdeb,  # Substitua pelo valor real
                anoMedicao=ano
            )
            session.add(ideb)
            
            # Notas SAEB (ajuste conforme os dados reais)
            notaMatematica = row[f'VL_NOTA_MATEMATICA_{ano}']
            notaMatematica = notaMatematica if notaMatematica not in ['-', 'ND', 'ND***'] else None
            notaPortugues = row[f'VL_NOTA_PORTUGUES_{ano}']
            notaPortugues = notaPortugues if notaPortugues not in ['-', 'ND', 'ND***'] else None
            notaPadronizada = row[f'VL_NOTA_MEDIA_{ano}']
            notaPadronizada = notaPadronizada if notaPadronizada not in ['-', 'ND', 'ND***'] else None
            saeb = NotaSAEB(
                idEscola=str(row['ID_ESCOLA']),
                notaMatematica=notaMatematica,  # Substitua pelo valor real
                notaLinguaPort=notaPortugues,  # Substitua pelo valor real
                notaPadronizada=notaPadronizada,  # Substitua pelo valor real
                anoMedicao=ano
            )
            session.add(saeb)
        print(f'{counter}: Notas SAEB e IDEB {ideb.idEscola} inserida!')
        counter += 1

    print('Notas inseridos!')


if __name__ == '__main__':
    carregar_dados()
    print("Dados carregados com sucesso!")