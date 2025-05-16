SELECT 
    e.uf,
    est.nome AS nome_estado,
    AVG(saeb."notaMatematica") AS media_matematica,
    AVG(saeb."notaLinguaPort") AS media_portugues,
    SUM(se.media_se * se.total_alunos) / SUM(se.total_alunos) AS media_ponderada_se
FROM 
    public."Escola" esc
JOIN 
    public."Municipio" e ON esc."idMunicipio" = e."idMunicipio"
JOIN 
    public."Estado" est ON e.uf = est.uf
JOIN 
    public."NotaSAEB" saeb ON saeb."idEscola" = esc."idEscola"
JOIN (
    SELECT 
        ia."idEscola",
        SUM(pca."porcentagemAlunos" * cse."idClassificacaoSE") / 100.0 AS media_se,
        SUM(ia."qtdAlunosInse") AS total_alunos
    FROM 
        public."IndicadoresAlunos" ia
    JOIN 
        public."PorcentagemClassificacaoAlunos" pca ON ia."idIndicadoresAlunos" = pca."idIndicadoresAlunos"
    JOIN 
        public."ClassificacaoSocioEconomica" cse ON pca."idClassificacaoSE" = cse."idClassificacaoSE"
    GROUP BY 
        ia."idEscola"
) se ON se."idEscola" = esc."idEscola"
WHERE 
    esc."idTipoLocalizacao" = (
        SELECT "idTipoLocalizacao" 
        FROM public."TipoLocalizacao" 
        WHERE LOWER("nomeTipoLocalizacao") LIKE '%rural%'
        LIMIT 1
    )
GROUP BY 
    e.uf, est.nome
ORDER BY 
    est.nome;