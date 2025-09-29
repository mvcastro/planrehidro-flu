Foram excluídas do inventário (Tabela inventario_estacoes_flu_ana) todas as estações
que fazem parte do HIDROOBSERVA com exceção daquelas operadas pela SGB-CPRM

```SQL

    SELECT est.*
    FROM Estacao est
    INNER JOIN Entidade rsp ON rsp.Codigo = est.ResponsavelCodigo
    INNER JOIN Entidade opr ON opr.Codigo = est.OperadoraCodigo
    WHERE TipoEstacao = 1
		AND rsp.Sigla = 'ANA' 
        AND Operando = 1 
        AND Descricao NOT LIKE '%HIDROOBSERVA%'

    UNION ALL
    
    SELECT est.*
    FROM Estacao est
    INNER JOIN Entidade rsp ON rsp.Codigo = est.ResponsavelCodigo
    INNER JOIN Entidade opr ON opr.Codigo = est.OperadoraCodigo
    WHERE TipoEstacao = 1
		AND rsp.Sigla = 'ANA'
        AND opr.Sigla = 'SGB-CPRM'
        AND Descricao LIKE '%HIDROOBSERVA%'

```