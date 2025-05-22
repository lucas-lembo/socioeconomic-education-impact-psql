SELECT
    m.uf,
    est.nome AS nome_estado,
    saeb."anoMedicao",
    ROUND(AVG(saeb."notaPadronizada")::numeric, 2) AS media_nota_saeb,
    ROUND(AVG(taxas.total)::numeric, 2) AS media_taxa_aprovacao
FROM public."NotaSAEB" saeb
JOIN public."Escola" e ON saeb."idEscola" = e."idEscola"
JOIN public."Municipio" m ON e."idMunicipio" = m."idMunicipio"
JOIN public."Estado" est ON m.uf = est.uf
JOIN public."TaxasAprovacao" taxas ON taxas."idEscola" = e."idEscola" AND taxas."anoMedicao" = saeb."anoMedicao"
WHERE saeb."anoMedicao" IN (2017, 2019, 2021, 2023)
GROUP BY m.uf, est.nome, saeb."anoMedicao"
ORDER BY m.uf, saeb."anoMedicao";
