PREFIX schema: <http://schema.org/>
PREFIX admin: <https://schema.ld.admin.ch/>
SELECT ?company_uri ?name ?company_type ?municipality ?description
WHERE {
  ?company_uri a admin:ZefixOrganisation ;
       schema:name ?name ;
       admin:municipality ?muni_id ;
       schema:description ?description .
  ?muni_id schema:name ?municipality .
  ?company_uri schema:additionalType ?type_id .
  ?type_id schema:name ?company_type .

  FILTER langMatches(lang(?name), "de") .
  FILTER langMatches(lang(?company_type), "de") .
  FILTER NOT EXISTS {
    FILTER (
      CONTAINS(LCASE(?description), "crypto") || 
      CONTAINS(LCASE(?description), "krypto") || 
      CONTAINS(LCASE(?description), "blockchain") || 
      CONTAINS(LCASE(?description), "dlt") || 
      CONTAINS(LCASE(?description), "bitcoin") || 
      CONTAINS(LCASE(?description), "token") || 
      CONTAINS(LCASE(?description), "nft")
    )
  }
} 
LIMIT 50
