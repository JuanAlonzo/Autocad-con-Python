"""
Script de Prueba: Insertar Bloque en Crudo (Diagnóstico de Escala)
"""

from pyautocad import APoint
from utilities import require_autocad, ConsoleUI

# HARDCODED
BLOQUE_NOMBRE = "UBICACION POSTES UTM"
CAPA_TEST = "0"

ui = ConsoleUI()


def main():
    acad = require_autocad(ui)
    doc = acad.doc
    msp = doc.ModelSpace

    try:
        doc.StartUndoMark()

        try:
            doc.Blocks.Item(BLOQUE_NOMBRE)
            ui.show_message(
                f"Bloque '{BLOQUE_NOMBRE}' encontrado en la biblioteca.", "success"
            )
        except Exception:
            ui.show_message(
                f"ERROR CRÍTICO: El bloque '{BLOQUE_NOMBRE}' NO existe en este dibujo.",
                "error",
            )
            return

        # Punto de inserción
        # Usaremos una coordenada fija (Modificable)
        punto_base = [3000.0, 1400.0, 0.0]

        ui.show_message(
            f"Insertando pruebas en coordenadas aprox: {punto_base}", "info"
        )

        # --- PRUEBA 1: Escala 1.0 (La que sale gigante) ---
        try:
            p1 = APoint(punto_base[0], punto_base[1])
            blk1 = msp.InsertBlock(p1, BLOQUE_NOMBRE, 1, 1, 1, 0)
            blk1.Layer = CAPA_TEST
            ui.show_message(
                f"1. Bloque insertado (Escala 1.0). Handle: {blk1.Handle}", "warning"
            )
        except Exception as e:
            ui.show_message(f"Fallo inserción 1: {e}", "error")

        # --- PRUEBA 2: Escala 1/250 (0.004) ---
        # Si dices que sale 250 veces más grande, esta debería ser la correcta.
        try:
            p2 = APoint(punto_base[0] + 50, punto_base[1])  # 50m a la derecha
            scale_inv = 1.0 / 250.0  # 0.004
            blk2 = msp.InsertBlock(
                p2, BLOQUE_NOMBRE, scale_inv, scale_inv, scale_inv, 0
            )
            blk2.Layer = CAPA_TEST
            ui.show_message(
                f"2. Bloque insertado (Escala 1/250 = {scale_inv}). Handle: {blk2.Handle}",
                "success",
            )
        except Exception as e:
            ui.show_message(f"Fallo inserción 2: {e}", "error")

        # --- PRUEBA 3: Escala 0.001 (Conversión MM a M) ---
        try:
            p3 = APoint(punto_base[0] + 100, punto_base[1])  # 100m a la derecha
            blk3 = msp.InsertBlock(p3, BLOQUE_NOMBRE, 0.001, 0.001, 0.001, 0)
            blk3.Layer = CAPA_TEST
            ui.show_message(
                f"3. Bloque insertado (Escala 0.001). Handle: {blk3.Handle}", "info"
            )
        except Exception as e:
            ui.show_message(f"Fallo inserción 3: {e}", "error")

        ui.show_message("Prueba finalizada. Revisa en AutoCAD cuál se ve bien.", "info")
    except Exception as e:
        ui.show_message(f"Error: {e}", "error")
        doc.SendCommand("_UNDO 1 ")
    finally:
        doc.EndUndoMark()


if __name__ == "__main__":
    main()
