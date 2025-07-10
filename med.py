
import math

def entidades_para_polilinhas(msp):
    # Converter LINE para LWPOLYLINE
    for e in list(msp.query('LINE')):
        points = [e.dxf.start, e.dxf.end]
        msp.add_lwpolyline(points)
        msp.delete_entity(e)

    # Converter CIRCLE para LWPOLYLINE (aproximação por 36 segmentos)
    for e in list(msp.query('CIRCLE')):
        center = e.dxf.center
        radius = e.dxf.radius
        segments = 36
        points = [
            (
                center.x + radius * math.cos(2 * math.pi * i / segments),
                center.y + radius * math.sin(2 * math.pi * i / segments)
            )
            for i in range(segments)
        ]
        msp.add_lwpolyline(points, close=True)
        msp.delete_entity(e)

    # Converter SPLINE para LWPOLYLINE (amostragem de pontos)
    for e in list(msp.query('SPLINE')):
        try:
            points = [tuple(p) for p in e.approximate(50)]
            msp.add_lwpolyline(points)
            msp.delete_entity(e)
        except Exception:
            pass

import ezdxf
import shutil
import os
import re
import traceback
import sys

def limpar_nome(nome):
    return re.sub(r'[<>:"/\\|?*]', '_', nome)

def obter_dimensoes_lwpolyline(path):
    try:
        import math
        doc = ezdxf.readfile(path)
        msp = doc.modelspace()

        # Converter entidades para polilinhas
        entidades_para_polilinhas(msp)

        min_x, min_y = float("inf"), float("inf")
        max_x, max_y = float("-inf"), float("-inf")
        contou = 0

        for entidade in msp.query("LWPOLYLINE"):
            for ponto in entidade:
                x, y = ponto[0], ponto[1]
                min_x = min(min_x, x)
                min_y = min(min_y, y)
                max_x = max(max_x, x)
                max_y = max(max_y, y)
                contou += 1

        if contou == 0:
            return None

        largura = max_x - min_x
        altura = max_y - min_y

        return round(largura), round(altura)

    except Exception as e:
        print(f"❌ Erro ao ler '{os.path.basename(path)}': {e}")
        traceback.print_exc()
        return None

def processar_pasta_dxf():
    try:
        pasta = os.path.dirname(os.path.abspath(sys.argv[0]))  # Caminho do .exe ou script
        arquivos = [f for f in os.listdir(pasta) if f.lower().endswith('.dxf')]
        destino = os.path.join(pasta, "dxfs")
        os.makedirs(destino, exist_ok=True)

        if not arquivos:
            print("⚠️ Nenhum arquivo DXF foi encontrado na mesma pasta do programa.")
            input("Pressione ENTER para sair.")
            return

        print(f"📁 {len(arquivos)} arquivo(s) DXF encontrado(s). Iniciando processamento...\n")

        for nome_arquivo in arquivos:
            try:
                caminho_original = os.path.join(pasta, nome_arquivo)
                dimensoes = obter_dimensoes_lwpolyline(caminho_original)

                if dimensoes is None:
                    print(f"⚠️  Ignorado: {nome_arquivo} (sem LWPOLYLINE válida)")
                    continue

                largura, altura = dimensoes
                base, ext = os.path.splitext(nome_arquivo)
                novo_nome = limpar_nome(f"{base}_{largura}x{altura}{ext}")
                novo_path = os.path.join(destino, novo_nome)

                shutil.copyfile(caminho_original, novo_path)
                print(f"✅ {nome_arquivo} → dxfs/{novo_nome}")

            except Exception as erro_arquivo:
                print(f"❌ Erro ao processar {nome_arquivo}: {erro_arquivo}")
                traceback.print_exc()

        print("\n🚀 Finalizado! Os arquivos renomeados estão na pasta 'dxfs'.")
        input("Pressione ENTER para sair.")

    except Exception as erro_geral:
        print(f"\n❌ ERRO GERAL: {erro_geral}")
        traceback.print_exc()
        input("Pressione ENTER para sair.")

if __name__ == "__main__":
    processar_pasta_dxf()
