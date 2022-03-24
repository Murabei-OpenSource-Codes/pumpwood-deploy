datalake_attribute_descriptions = {
   "total": {
      "description": "{metric}__!{source}",
      "notes": "{notes}"
   },
   "by_post": {
      "description": "{metric}__{source}__!{post_id}",
      "notes": "{notes} post id: {post_id}"
   }
}


datalake_attributes = {
   "fan_count": {
      "dimensions": {
         "metric": "fan_count",
         "source": "facebook_open"
      },
      "notes": "The number of users who like the Page. "
               "For Global Pages this is the count for all Pages across the brand.",
      "type_id": "TIME_DISCR"
   },
   "fan_delta": {
      "dimensions": {
         "metric": "fan_delta",
         "source": "facebook_open"
      },
      "notes": "One day difference of the number of users who like the Page. "
               "For Global Pages this is the count for all Pages across the brand.",
      "type_id": "TIME_DISCR"
   },
   "talking_about_count": {
      "dimensions": {
         "metric": "talking_about_count",
         "source": "facebook_open"
      },
      "notes": "The number of people talking about the Page",
      "type_id": "TIME_DISCR"
   },
   "talking_about_delta": {
      "dimensions": {
         "metric": "talking_about_delta",
         "source": "facebook_open"
      },
      "notes": "One day difference of the number of people talking about the Page",
      "type_id": "TIME_DISCR"
   },
   "comments_count": {
      "dimensions": {
         "metric": "comments_count",
         "source": "facebook_open"
      },
      "notes": "Total count of comments of the page",
      "type_id": "TIME_DISCR"
   },
   "comments_delta": {
      "dimensions": {
         "metric": "comments_delta",
         "source": "facebook_open"
      },
      "notes": "One day difference of total count of comments of the page",
      "type_id": "TIME_DISCR"
   },
   "haha_count": {
      "dimensions": {
         "metric": "haha_count",
         "source": "facebook_open"
      },
      "notes": "Total count of haha reactions of the page",
      "type_id": "TIME_DISCR"
   },
   "haha_delta": {
      "dimensions": {
         "metric": "haha_delta",
         "source": "facebook_open"
      },
      "notes": "One day difference of total count of haha reactions of the page",
      "type_id": "TIME_DISCR"
   },
   "like_count": {
      "dimensions": {
         "metric": "like_count",
         "source": "facebook_open"
      },
      "notes": "Total count of likes of the page",
      "type_id": "TIME_DISCR"
   },
   "like_delta": {
      "dimensions": {
         "metric": "like_delta",
         "source": "facebook_open"
      },
      "notes": "One day difference of total count of likes of the page",
      "type_id": "TIME_DISCR"
   },
   "love_count": {
      "dimensions": {
         "metric": "love_count",
         "source": "facebook_open"
      },
      "notes": "Total count of love reactions of the page",
      "type_id": "TIME_DISCR"
   },
   "love_delta": {
      "dimensions": {
         "metric": "love_delta",
         "source": "facebook_open"
      },
      "notes": "One day difference of total count of love reactions of the page",
      "type_id": "TIME_DISCR"
   },
   "sad_count": {
      "dimensions": {
         "metric": "sad_count",
         "source": "facebook_open"
      },
      "notes": "Total count of sad reactions of the page",
      "type_id": "TIME_DISCR"
   },
   "sad_delta": {
      "dimensions": {
         "metric": "sad_delta",
         "source": "facebook_open"
      },
      "notes": "One day difference of total count of sad reactions of the page",
      "type_id": "TIME_DISCR"
   },
   "shares_count": {
      "dimensions": {
         "metric": "shares_count",
         "source": "facebook_open"
      },
      "notes": "Total count of shares of the page",
      "type_id": "TIME_DISCR"
   },
   "shares_delta": {
      "dimensions": {
         "metric": "shares_delta",
         "source": "facebook_open"
      },
      "notes": "One day difference of total count of shares of the page",
      "type_id": "TIME_DISCR"
   },
   "angry_count": {
      "dimensions": {
         "metric": "angry_count",
         "source": "facebook_open"
      },
      "notes": "Total count of angry reactions of the page",
      "type_id": "TIME_DISCR"
   },
   "angry_delta": {
      "dimensions": {
         "metric": "angry_delta",
         "source": "facebook_open"
      },
      "notes": "One day difference of total count of angry reactions of the page",
      "type_id": "TIME_DISCR"
   },
   "wow_count": {
      "dimensions": {
         "metric": "wow_count",
         "source": "facebook_open"
      },
      "notes": "Total count of wow reactions of the page",
      "type_id": "TIME_DISCR"
   },
   "wow_delta": {
      "dimensions": {
         "metric": "wow_delta",
         "source": "facebook_open"
      },
      "notes": "One day difference of total count of wow reactions of the page",
      "type_id": "TIME_DISCR"
   }
}


datalake_modeling_unit_descriptions = {
   "company": "!{artist}"
}


datalake_modeling_units = {
   "fernando & sorocaba": {"dimensions": {"artist": "fernando_e_sorocaba"}},
   "antony & gabriel": {"dimensions": {"artist": "antony_e_gabriel"}},
   "bruninho & davi": {"dimensions": {"artist": "bruninho_e_davi"}},
   "bruno & barretto": {"dimensions": {"artist": "bruno_e_barretto"}},
   "bruno & caio cesar": {"dimensions": {"artist": "bruno_e_caio_cesar"}},
   "bruno & marrone": {"dimensions": {"artist": "bruno_e_marrone"}},
   "carlos & jader": {"dimensions": {"artist": "carlos_e_jader"}},
   "carreiro & capataz": {"dimensions": {"artist": "carreiro_e_capataz"}},
   "césar menotti & fabiano": {"dimensions": {"artist": "césar_menotti_e_fabiano"}},
   "chitãozinho & xororó": {"dimensions": {"artist": "chitãozinho_e_xororó"}},
   "chrystian & ralf": {"dimensions": {"artist": "chrystian_e_ralf"}},
   "cleber & cauan": {"dimensions": {"artist": "cleber_e_cauan"}},
   "daniel": {"dimensions": {"artist": "daniel"}},
   "day & lara": {"dimensions": {"artist": "day_e_lara"}},
   "diego & arnaldo": {"dimensions": {"artist": "diego_e_arnaldo"}},
   "diego & marcel": {"dimensions": {"artist": "diego_e_marcel"}},
   "diego & victor hugo": {"dimensions": {"artist": "diego_e_victor_hugo"}},
   "dorgival dantas": {"dimensions": {"artist": "dorgival_dantas"}},
   "edson & hudson": {"dimensions": {"artist": "edson_e_hudson"}},
   "eduardo costa": {"dimensions": {"artist": "eduardo_costa"}},
   "felipe araújo": {"dimensions": {"artist": "felipe_araújo"}},
   "fernanda costa": {"dimensions": {"artist": "fernanda_costa"}},
   "fiduma & jeca": {"dimensions": {"artist": "fiduma_e_jeca"}},
   "fred & gustavo": {"dimensions": {"artist": "fred_e_gustavo"}},
   "gabriel diniz": {"dimensions": {"artist": "gabriel_diniz"}},
   "george henrique & rodrigo": {"dimensions": {"artist": "george_henrique_e_rodrigo"}},
   "gino & geno": {"dimensions": {"artist": "gino_e_geno"}},
   "guilherme & santiago": {"dimensions": {"artist": "guilherme_e_santiago"}},
   "gustavo mioto": {"dimensions": {"artist": "gustavo_mioto"}},
   "gusttavo lima": {"dimensions": {"artist": "gusttavo_lima"}},
   "henrique & diego": {"dimensions": {"artist": "henrique_e_diego"}},
   "henrique & juliano": {"dimensions": {"artist": "henrique_e_juliano"}},
   "higor rocha": {"dimensions": {"artist": "higor_rocha"}},
   "hugo & guilherme": {"dimensions": {"artist": "hugo_e_guilherme"}},
   "hugo & tiago": {"dimensions": {"artist": "hugo_e_tiago"}},
   "hugo del vecchio": {"dimensions": {"artist": "hugo_del_vecchio"}},
   "hugo henrique": {"dimensions": {"artist": "hugo_henrique"}},
   "hugo pena & gabriel": {"dimensions": {"artist": "hugo_pena_e_gabriel"}},
   "humberto & ronaldo": {"dimensions": {"artist": "humberto_e_ronaldo"}},
   "israel & rodolffo": {"dimensions": {"artist": "israel_e_rodolffo"}},
   "israel novaes": {"dimensions": {"artist": "israel_novaes"}},
   "jads & jadson": {"dimensions": {"artist": "jads_e_jadson"}},
   "jefferson moraes": {"dimensions": {"artist": "jefferson_moraes"}},
   "joão bosco & vinícius": {"dimensions": {"artist": "joão_bosco_e_vinícius"}},
   "joão carreiro & capataz": {"dimensions": {"artist": "joão_carreiro_e_capataz"}},
   "joão marcio & fabiano": {"dimensions": {"artist": "joão_marcio_e_fabiano"}},
   "joão mineiro & marciano": {"dimensions": {"artist": "joão_mineiro_e_marciano"}},
   "joão neto & frederico": {"dimensions": {"artist": "joão_neto_e_frederico"}},
   "jorge & mateus": {"dimensions": {"artist": "jorge_e_mateus"}},
   "julia & rafaela": {"dimensions": {"artist": "julia_e_rafaela"}},
   "kléo dibah & rafael": {"dimensions": {"artist": "kléo_dibah_e_rafael"}},
   "léo & raphael": {"dimensions": {"artist": "léo_e_raphael"}},
   "léo magalhães": {"dimensions": {"artist": "léo_magalhães"}},
   "leonardo": {"dimensions": {"artist": "leonardo"}},
   "loubet": {"dimensions": {"artist": "loubet"}},
   "luan santana": {"dimensions": {"artist": "luan_santana"}},
   "lucas lucco": {"dimensions": {"artist": "lucas_lucco"}},
   "luiz henrique & léo": {"dimensions": {"artist": "luiz_henrique_e_léo"}},
   "luiza & maurílio": {"dimensions": {"artist": "luiza_e_maurílio"}},
   "maiara & maraisa": {"dimensions": {"artist": "maiara_e_maraisa"}},
   "mano walter": {"dimensions": {"artist": "mano_walter"}},
   "marcos & belutti": {"dimensions": {"artist": "marcos_e_belutti"}},
   "marcos & fernando": {"dimensions": {"artist": "marcos_e_fernando"}},
   "maria cecília & rodolfo": {"dimensions": {"artist": "maria_cecília_e_rodolfo"}},
   "marília mendonça": {"dimensions": {"artist": "marília_mendonça"}},
   "matheus & kauan": {"dimensions": {"artist": "matheus_e_kauan"}},
   "matogrosso & mathias": {"dimensions": {"artist": "matogrosso_e_mathias"}},
   "michel teló": {"dimensions": {"artist": "michel_teló"}},
   "milionário & josé rico": {"dimensions": {"artist": "milionário_e_josé_rico"}},
   "munhoz & mariano": {"dimensions": {"artist": "munhoz_e_mariano"}},
   "naiara azevedo": {"dimensions": {"artist": "naiara_azevedo"}},
   "paula fernandes": {"dimensions": {"artist": "paula_fernandes"}},
   "paula mattos": {"dimensions": {"artist": "paula_mattos"}},
   "pedro & benício": {"dimensions": {"artist": "pedro_e_benício"}},
   "pedro paulo & alex": {"dimensions": {"artist": "pedro_paulo_e_alex"}},
   "rick & rangel": {"dimensions": {"artist": "rick_e_rangel"}},
   "rick & renner": {"dimensions": {"artist": "rick_e_renner"}},
   "rionegro & solimões": {"dimensions": {"artist": "rionegro_e_solimões"}},
   "roberta miranda": {"dimensions": {"artist": "roberta_miranda"}},
   "simone & simaria": {"dimensions": {"artist": "simone_e_simaria"}},
   "solange almeida": {"dimensions": {"artist": "solange_almeida"}},
   "teodoro & sampaio": {"dimensions": {"artist": "teodoro_e_sampaio"}},
   "thaeme & thiago": {"dimensions": {"artist": "thaeme_e_thiago"}},
   "thiago brava": {"dimensions": {"artist": "thiago_brava"}},
   "victor & léo": {"dimensions": {"artist": "victor_e_léo"}},
   "villa baggage": {"dimensions": {"artist": "villa_baggage"}},
   "wesley safadão": {"dimensions": {"artist": "wesley_safadão"}},
   "zé felipe": {"dimensions": {"artist": "zé_felipe"}},
   "zé henrique & gabriel": {"dimensions": {"artist": "zé_henrique_e_gabriel"}},
   "zé neto & cristiano": {"dimensions": {"artist": "zé_neto_e_cristiano"}},
   "zezé di camargo & luciano": {"dimensions": {"artist": "zezé_di_camargo_e_luciano"}},
   "anitta": {"dimensions": {"artist": "anitta"}}
}


datalake_geoarea_descriptions = {
   "country": "!{country}"
}


datalake_geoareas = {
   "BR": {
      "dimensions": {
         "country": "brazil"
      }
   }
}
