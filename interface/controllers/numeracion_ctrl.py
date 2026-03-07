from utilities.cad_manager import cad
from interface.workers.numeracion_worker import NumeracionWorker


class NumeracionController:
    def __init__(self, main_controller):
        self.main = main_controller
        self.view = None
        self.worker = None

    def set_view(self, view):
        self.view = view

    def ejecutar_numeracion(self):
        cad.connect()

        if not cad.is_connected:
            self.main.log("ERROR: AutoCAD no está conectado.")
            return

        cfg = self.view.get_numeracion_config()
        estrategia = cfg.get("estrategia")

        # Validación dinámica basada en el Patrón Estrategia
        if estrategia == "DFS":
            if not cfg.get("dict_red") or not cfg.get("dict_postes"):
                self.main.log(
                    "ERROR: El perfil DFS requiere capas de red y postes definidos en settings.json."
                )
                return
        elif estrategia == "SIMPLE":
            if not cfg.get("dict_postes"):
                self.main.log(
                    "ERROR: El perfil SIMPLE requiere tipos de poste definidos en settings.json."
                )
                return
        else:
            self.main.log(
                "ERROR: Perfil no válido. Verifica que settings.json tenga la estructura correcta."
            )
            return

        self.main.log(f"--- INICIANDO NUMERACIÓN (Perfil: {cfg.get('perfil_id')}) ---")
        # Bloqueo temporal de UI y solicitud de interacción con AutoCAD
        self.view.set_execution_state(is_running=True)
        self.main.view.hide()

        punto_clic = None
        try:
            try:
                cad.app.Visible = True
            except Exception:
                pass

            self.main.log("Esperando clic del usuario en AutoCAD...")

            # Llamada síncrona en el hilo principal
            punto_com = cad.doc.Utility.GetPoint(
                Prompt="\nSeleccione el poste/punto de inicio para la numeración: "
            )
            punto_clic = (round(punto_com[0], 4), round(punto_com[1], 4))

            self.main.log(f"Clic capturado en coordenadas: {punto_clic}")

        except Exception as e:
            self.main.log(f"Selección cancelada o fallida: {e}")
            self.view.set_execution_state(is_running=False)
            self.main.view.show()
            return

        # Restauración de UI e inyección de datos al Worker
        self.main.view.show()
        cfg["punto_inicio"] = punto_clic

        # Lanzamiento del hilo secundario
        self.worker = NumeracionWorker(cfg)
        self.worker.progress_signal.connect(self.view.update_progress)
        self.worker.log_signal.connect(self.main.log)
        self.worker.finished_signal.connect(self.on_numeracion_finished)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.start()

    def on_numeracion_finished(self, success: bool):
        self.view.set_execution_state(is_running=False)
        if success:
            self.main.log("--- NUMERACIÓN COMPLETADA CON ÉXITO ---")
        else:
            self.main.log("--- LA NUMERACIÓN FINALIZÓ CON ERRORES ---")
