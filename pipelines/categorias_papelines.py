from bson import ObjectId

def pipeline_categorias_con_retos():
    return [
        {
            "$lookup": {
                "from": "retos",
                "localField": "_id",
                "foreignField": "id_categoria",
                "as": "retos"
            }
        },
        {
            "$project": {
                "id": {"$toString": "$_id"},
                "name": 1,
                "text": 1,
                "total_retos": {"$size": "$retos"},
                "retos": {
                    "$map": {
                        "input": "$retos",
                        "as": "reto",
                        "in": {
                            "name": "$$reto.name",
                            "puntos": "$$reto.puntos"
                        }
                    }
                }
            }
        }
    ]

def pipeline_estadisticas_categoria(categoria_id: str) -> list:
    return [
        {
            "$match": {
                "id_categoria": ObjectId(categoria_id)
            }
        },
        {
            "$group": {
                "_id": "$id_categoria",
                "total_retos": {"$sum": 1},
                "promedio_puntos": {"$avg": "$puntos"}
            }
        },
        {
            "$project": {
                "id_categoria": {"$toString": "$_id"},
                "total_retos": 1,
                "promedio_puntos": 1
            }
        }
    ]
    
    

def pipeline_validar_eliminacion_categoria(categoria_id: str) -> list:
    return [
        {
            "$match": {
                "_id": ObjectId(categoria_id)
            }
        },
        {
            "$lookup": {
                "from": "retos",
                "localField": "_id",
                "foreignField": "id_categoria",
                "as": "retos"
            }
        },
        {
            "$project": {
                "id": {"$toString": "$_id"},
                "name": 1,
                "cantidad_retos": {"$size": "$retos"}
            }
        }
    ]