from datetime import datetime, timedelta
import math
import networkx as nx  # type: ignore

# Classes


class Entrega:
    def __init__(self, destino, prazo, volume):
        self.destino = destino
        self.prazo = datetime.strptime(prazo, "%Y-%m-%d")
        self.volume = volume

    def __repr__(self):
        return f"Entrega(destino={self.destino}, prazo={self.prazo.date()}, volume={self.volume})"


class Caminhao:
    def __init__(self, id, capacidade, limite_horas):
        self.id = id
        self.capacidade = capacidade
        self.limite_horas = limite_horas
        self.carga_atual = 0
        self.horas_usadas = 0
        self.entregas = []
        self.centro = None

    def carregar(self, entrega):
        if self.carga_atual + entrega.volume <= self.capacidade:
            self.carga_atual += entrega.volume
            self.entregas.append(entrega)
            return True
        return False

    def pode_operar(self, horas):
        return self.horas_usadas + horas <= self.limite_horas

    def __repr__(self):
        return f"{self.id} | Carga: {self.carga_atual}kg | Entregas: {len(self.entregas)}"

# Funções auxiliares


def haversine(coord1, coord2):
    R = 6371
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def mostrar_rota(origem, destino):
    try:
        caminho = nx.shortest_path(
            grafo, source=origem, target=destino, weight='weight')
        return f"Rota: {' -> '.join(caminho)}"
    except nx.NetworkXNoPath:
        return f"Sem rota entre {origem} e {destino}"


def centro_mais_proximo(destino, limite=1500):
    menor = float("inf")
    escolhido = None
    for centro in centros:
        dist = haversine(coordenadas[centro], coordenadas[destino])
        if dist < menor and dist <= limite:
            menor = dist
            escolhido = centro
    return escolhido, menor


# Coordenadas
coordenadas = {
    "Belem": (-1.4558, -48.5044),
    "Recife": (-8.0476, -34.8770),
    "Brasilia": (-15.7939, -47.8828),
    "Sao_Paulo": (-23.5505, -46.6333),
    "Florianopolis": (-27.5949, -48.5480),
    "Santarem": (-2.4385, -54.6996),
    "Maraba": (-5.3686, -49.1170),
    "Macapa": (0.0349, -51.0694),
    "Joao_Pessoa": (-7.1150, -34.8631),
    "Maceio": (-9.6498, -35.7089),
    "Natal": (-5.7945, -35.2110),
    "Anapolis": (-16.3285, -48.9526),
    "Uberlandia": (-18.9186, -48.2772),
    "Campo_Grande": (-20.4697, -54.6201),
    "Campinas": (-22.9099, -47.0626),
    "Sorocaba": (-23.5015, -47.4526),
    "Ribeirao_Preto": (-21.1784, -47.8069),
    "Lages": (-27.8150, -50.3259),
    "Joinville": (-26.3045, -48.8487),
    "Pelotas": (-31.7654, -52.3371),
    "Porto_Alegre": (-30.0346, -51.2177),
    "Chapeco": (-27.1004, -52.6152),
    "Curitiba": (-25.4284, -49.2733),
}

centros = ["Belem", "Recife", "Brasilia", "Sao_Paulo", "Florianopolis"]

quantidade_caminhoes_por_centro = {
    "Belem": {"pequeno": 2, "medio": 1, "grande": 1},
    "Recife": {"pequeno": 3, "medio": 1, "grande": 1},
    "Brasilia": {"pequeno": 2, "medio": 2, "grande": 2},
    "Sao_Paulo": {"pequeno": 4, "medio": 2, "grande": 3},
    "Florianopolis": {"pequeno": 3, "medio": 3, "grande": 2},
}

grafo = nx.Graph()
#
# Conecta centros
for i in range(len(centros)):
    for j in range(i + 1, len(centros)):
        c1, c2 = centros[i], centros[j]
        dist = haversine(coordenadas[c1], coordenadas[c2])
        grafo.add_edge(c1, c2, weight=dist)

# Conecta destinos aos centros mais próximos
for cidade in coordenadas:
    if cidade not in grafo.nodes:
        centro, dist = centro_mais_proximo(cidade, 2000)
        if centro:
            grafo.add_edge(centro, cidade, weight=dist)

# Entregas
cenarios = {
    "Belem": ["Santarem", "Maraba", "Macapa"],
    "Recife": ["Joao_Pessoa", "Maceio", "Natal"],
    "Brasilia": ["Anapolis", "Uberlandia", "Campo_Grande"],
    "Sao_Paulo": ["Campinas", "Sorocaba", "Ribeirao_Preto"],
    "Florianopolis": ["Lages", "Joinville", "Pelotas", "Porto_Alegre", "Chapeco", "Curitiba"]
}

entregas = []
for centro, destinos in cenarios.items():
    for i, destino in enumerate(destinos):
        prazo = f"2025-06-{(i + 2):02d}"
        volume = 600 + (i % 3) * 100  # alterna entre 600, 700, 800
        entregas.append(Entrega(destino, prazo, volume))

tipos_caminhoes = {
    "pequeno": {"capacidade": 600, "limite_horas": 8},
    "medio": {"capacidade": 800, "limite_horas": 12},
    "grande": {"capacidade": 1200, "limite_horas": 22},
}

caminhoes = []
for centro in centros:
    config = quantidade_caminhoes_por_centro.get(centro, {})
    for tipo, quantidade in config.items():
        for i in range(quantidade):
            caminh = Caminhao(
                id=f"{centro}_{tipo.upper()}_{i+1}",
                capacidade=tipos_caminhoes[tipo]["capacidade"],
                limite_horas=tipos_caminhoes[tipo]["limite_horas"],
            )
            caminh.centro = centro
            caminhoes.append(caminh)

# Alocação
log = []
resumo = {}

inicio_entregas = datetime(2025, 6, 1)
for entrega in entregas:
    centro, distancia = centro_mais_proximo(entrega.destino)
    if not centro:
        log.append(f"Entrega para {entrega.destino} não alocada (sem rota).")
        continue

    tempo = distancia / 60  # horas estimadas
    data_entrega = inicio_entregas + timedelta(hours=tempo)

    alocado = False
    for cam in caminhoes:
        if cam.centro == centro and cam.carregar(entrega) and cam.pode_operar(tempo):
            cam.horas_usadas += tempo
            rota = mostrar_rota(centro, entrega.destino)
            log.append(
                f"{entrega.destino} entregue por {cam.id} via {centro}. "
                f"{rota} | Tempo estimado: {tempo:.1f}h | Data estimada: {data_entrega.strftime('%Y-%m-%d %H:%M')}"
            )

            if cam.id not in resumo:
                resumo[cam.id] = {'carga': cam.carga_atual, 'entregas': 1}
            else:
                resumo[cam.id]['entregas'] += 1
                resumo[cam.id]['carga'] = cam.carga_atual

            alocado = True
            break

    if not alocado:
        log.append(f"Entrega para {entrega.destino} não foi alocada.")

# Saída das entregas
print("\n".join(log))

# Resumo
print("\nResumo dos Caminhões:")
for caminhao, info in resumo.items():
    print(
        f"{caminhao} | Carga: {info['carga']}kg | Entregas: {info['entregas']}")
