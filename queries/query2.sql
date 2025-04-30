SELECT
    est.uf,
    est.nome AS estado,
    tl."nomeTipoLocalizacao" AS localizacao,
    ROUND(SUM(saeb."notaMatematica" * ia."qtdAlunosInse") / NULLIF(SUM(ia."qtdAlunosInse"), 0), 2) AS media_pond_matematica,
    ROUND(SUM(saeb."notaLinguaPort" * ia."qtdAlunosInse") / NULLIF(SUM(ia."qtdAlunosInse"), 0), 2) AS media_pond_portugues,
    ROUND(AVG(ia."qtdAlunosInse")::numeric, 2) AS media_indicador_socioeco
FROM "NotaSAEB" saeb
JOIN "Escola" e ON saeb."idEscola" = e."idEscola"
JOIN "Municipio" m ON e."idMunicipio" = m."idMunicipio"
JOIN "Estado" est ON m.uf = est.uf
JOIN "TipoLocalizacao" tl ON e."idTipoLocalizacao" = tl."idTipoLocalizacao"
JOIN "IndicadoresAlunos" ia ON ia."idEscola" = e."idEscola" AND ia."anoMedicao" = saeb."anoMedicao"
GROUP BY est.uf, est.nome, tl."nomeTipoLocalizacao"