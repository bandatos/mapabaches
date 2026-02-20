
#### Se busca obtener una base de datos de puntos de vialidades, se delimitó a la alcadía Cuautemoc.
### Se eligió esa alcaldia porque fue la alcaldía con mayor número de accidentes de ciclistas en 2019 (era el único año disponible)
### https://datos.cdmx.gob.mx/dataset/puntos-de-accidentes-de-ciclistas
### aunque dice que está actualizado al 2023, la base contiene solo de 2019


# Cargar librerías 
library(osmdata)   # Descarga de datos desde OpenStreetMap
library(sf)        # Manejo de datos espaciales
library(dplyr)     # Manipulación de datos
library(units)     # Manejo explícito de unidades métricas


# Obtener bounding box de la alcaldía Cuauhtémoc,  delimitamos para usar la capa gratuita de la API de google cloud

bb <- getbb("Cuauhtemoc, Ciudad de Mexico")



# Consultar únicamente vialidades primarias, para reducir el volumen de datos

calles <- opq(bb) %>%
  
    add_osm_feature(key = "highway",
                    value = c("primary"
                             # ,"secondary",
                              #"tertiary",
                              #"residential"
                             )) %>%
      osmdata_sf()
    
    
  

# Extraemos las geometrías tipo línea
vialidades <- calles$osm_lines


# Se transforma a UTM zona 14N (EPSG:32614), para trabajar con distancias en metros
vialidades_utm <- st_transform(vialidades, 32614)


# Calcular longitud de cada segmento (en metros)
longitudes <- st_length(vialidades_utm)

# Filtrar únicamente segmentos mayores a 350 metros
# Esto evita generar puntos redundantes en tramos muy cortos
vialidades_filtradas <- vialidades_utm[
  as.numeric(longitudes) > 350,
]


# Recalcular longitudes después del filtrado
longitudes <- st_length(vialidades_filtradas)

# Determinar número de puntos por segmento
# Se genera aproximadamente un punto cada 350 metros
n_puntos <- as.numeric(longitudes / 350)

# Garantizar al menos 1 punto por segmento
n_puntos[n_puntos < 1] <- 1

# Generar puntos equidistantes sobre cada línea
puntos <- st_line_sample(vialidades_filtradas, n = n_puntos)

# Convertir a objeto sf
puntos_sf <- st_sf(geometry = puntos)

# Regresar a sistema geográfico WGS84 (EPSG:4326)
# Necesario para usar con Google Street View API
puntos_wgs84 <- st_transform(puntos_sf, 4326)

# Visualización preliminar
plot(puntos_wgs84)

# contamos el total de puntos
length(puntos_wgs84$geometry)



# Extraemos coordenadas
coords <- st_coordinates(puntos_wgs84)

# Crear data frame con latitud y longitud
puntos_df <- data.frame(
  lon = coords[,1],
  lat = coords[,2]
)

# Exportar a CSV, después usaremos en python
write.csv(puntos_df, "puntos_cuauhtemoc.csv", row.names = FALSE)

