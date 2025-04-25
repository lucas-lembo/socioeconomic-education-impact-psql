import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, Double, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from constants import *
from psycopg2 import *


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
    df_inse = pd.read_excel('Planilha_INSE_Escolas.xlsx')
    df_divulgacao = pd.read_excel('Planilha_Divulgacao_EM.xlsx')
    
    # Processar dados e popular o banco
    processar_estados_municipios(df_inse)
    processar_escolas(df_inse)
    processar_indicadores(df_inse)
    processar_taxas_aprovacao(df_divulgacao)
    processar_notas(df_divulgacao)
    
    session.commit()

def processar_estados_municipios(df):
    # Processar estados
    estados = df[['SG_UF', 'NO_UF']].drop_duplicates()
    for _, row in estados.iterrows():
        estado = Estado(uf=row['SG_UF'], nome=row['NO_UF'])
        session.merge(estado)
    
    # Processar municípios
    municipios = df[['CO_MUNICIPIO', 'SG_UF', 'NO_MUNICIPIO', 'TP_CAPITAL']].drop_duplicates()
    for _, row in municipios.iterrows():
        municipio = Municipio(
            idMunicipio=str(row['CO_MUNICIPIO']),
            uf=row['SG_UF'],
            nome=row['NO_MUNICIPIO'],
            tipoCapital=classificar_tipo_capital(row['TP_CAPITAL'])
        )
        session.merge(municipio)

def classificar_tipo_capital(tipo):
    tipos = {
        1: "Capital",
        2: "Interior",
        3: "Outro"
    }
    return tipos.get(tipo, "Outro")

def processar_escolas(df):
    escolas = df[['ID_ESCOLA', 'CO_MUNICIPIO', 'NO_ESCOLA', 'TP_CAPITAL']].drop_duplicates()
    for _, row in escolas.iterrows():
        escola = Escola(
            idEscola=str(row['ID_ESCOLA']),
            idMunicipio=str(row['CO_MUNICIPIO']),
            nome=row['NO_ESCOLA'],
            tipoCapital=classificar_tipo_capital(row['TP_CAPITAL'])
        )
        session.merge(escola)

def processar_indicadores(df):
    # Primeiro, criar níveis de escolaridade (se necessário)
    niveis_escolaridade = {
        1: "Sem instrução",
        2: "Ensino Fundamental Incompleto",
        3: "Ensino Fundamental Completo",
        4: "Ensino Médio Incompleto",
        5: "Ensino Médio Completo",
        6: "Ensino Superior Incompleto",
        7: "Ensino Superior Completo",
        8: "Pós-graduação"
    }
    
    for id_nivel, descricao in niveis_escolaridade.items():
        nivel = NivelEscolariade(idEscolaridadePais=id_nivel, escolaridade=descricao)
        session.merge(nivel)
    
    # Processar classificações socioeconômicas
    for i in range(1, 9):
        classificacao = ClassificacaoSocioEconomica(
            idClassificacaoSE=i,
            qtdQuartos=0,  # Valores fictícios - ajuste conforme seus dados
            qtdCelulares=0,
            qtdGeladeiras=0,
            qtdTelevisores=0,
            qtdBanheiros=0,
            idEscolaridadePais=i
        )
        session.merge(classificacao)
    
    # Processar indicadores de alunos
    for _, row in df.iterrows():
        indicador = IndicadoresAlunos(
            idIndicadoresAlunos=int(row['ID_ESCOLA'] + str(row['NU_ANO_SAEB'])),
            qtdAlunosInse=row['QTD_ALUNOS_INSE'],
            anoMedicao=row['NU_ANO_SAEB'],
            idEscola=str(row['ID_ESCOLA'])
        )
        session.merge(indicador)
        
        # Processar porcentagens de classificação
        for nivel in range(1, 9):
            porcentagem = row[f'PC_NIVEL_{nivel}']
            if porcentagem > 0:
                porc_class = PorcentagemClassificacaoAlunos(
                    idPorcentagem=int(f"{row['ID_ESCOLA']}{row['NU_ANO_SAEB']}{nivel}"),
                    idIndicadoresAlunos=int(row['ID_ESCOLA'] + str(row['NU_ANO_SAEB'])),
                    idClassificacaoSE=nivel,
                    porcentagemAlunos=porcentagem
                )
                session.merge(porc_class)

def processar_taxas_aprovacao(df):
    # Esta função é um exemplo - ajuste conforme os dados reais da planilha Divulgacao EM
    for _, row in df.iterrows():
        taxa = TaxasAprovacao(
            idTaxasAprovacao=int(row['ID_ESCOLA'] + str(row['NU_ANO_SAEB'])),
            idEscola=str(row['ID_ESCOLA']),
            anoMedicao=row['NU_ANO_SAEB'],
            total=0  # Substitua pelo valor real se disponível
        )
        session.merge(taxa)
        
        # Exemplo para séries (ajuste conforme necessário)
        for serie in range(1, 6):
            aprovacao = AprovacaoSerie(
                idAprovacaoSerie=int(f"{row['ID_ESCOLA']}{row['NU_ANO_SAEB']}{serie}"),
                serie=serie,
                porcentagem=0,  # Substitua pelo valor real
                idTaxasAprovacao=int(row['ID_ESCOLA'] + str(row['NU_ANO_SAEB']))
            )
            session.merge(aprovacao)

def processar_notas(df):
    for _, row in df.iterrows():
        # Notas IDEB (ajuste conforme os dados reais)
        ideb = NotaIDEB(
            idIdeb=int(row['ID_ESCOLA'] + str(row['NU_ANO_SAEB'])),
            idEscola=str(row['ID_ESCOLA']),
            notaIdeb=0,  # Substitua pelo valor real
            anoMedicao=row['NU_ANO_SAEB']
        )
        session.merge(ideb)
        
        # Notas SAEB (ajuste conforme os dados reais)
        saeb = NotaSAEB(
            idSaeb=int(row['ID_ESCOLA'] + str(row['NU_ANO_SAEB'])),
            idEscola=str(row['ID_ESCOLA']),
            notaMatematica=0,  # Substitua pelo valor real
            notaLinguaPort=0,  # Substitua pelo valor real
            notaPadronizada=0,  # Substitua pelo valor real
            anoMedicao=row['NU_ANO_SAEB']
        )
        session.merge(saeb)

if __name__ == '':
    carregar_dados()
    print("Dados carregados com sucesso!")