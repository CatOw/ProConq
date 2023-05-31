import subprocess

from proconq.utils.constants import Paths
from proconq.src.backend.tracer.tracer_handler import TracerHandler
from proconq.src.frontend.frontend import Frontend
from proconq.setup_logging import setup_logging


class TracerUtils:
    logger = setup_logging(__name__)

    @staticmethod
    def get_valid_pids_by_name(process_name: str) -> list[str]:
        """
        Executes a subprocess that runs Linux's pidof.
        Returns list of pids that match, can be empty.
        """
        TracerUtils.logger.debug(f'Executing pidof {process_name}')
        pidof_proc = subprocess.run([Paths.PIDOF, process_name],
                                    stdout=subprocess.PIPE)
        
        pidof_result = pidof_proc.stdout.decode('utf-8')
        TracerUtils.logger.debug(f'pidof result: {pidof_result}')

        pids = pidof_result.split()
        for pid in pids:
            if not TracerUtils.is_pid_valid(pid):
                TracerUtils.logger.debug(f'pidof removing result {pid}')
                pids.remove(pid)

        TracerUtils.logger.debug(f'Final pidof result: {" ".join(pids)}')
        return pids
    
    @staticmethod
    def is_pid_valid(pid: str) -> bool:
        """
        Executes a subprocess that checks if PID is attachable
        by a ptrace tracer.
        """
        try:
            TracerUtils.logger.debug(f'Checking attachability of pid: {pid}')
            subprocess.check_call([Paths.CHECK_ATTACHABILITY, pid])
            TracerUtils.logger.debug(f'pid: {pid} attachability check succeeded')
            return True
        except subprocess.CalledProcessError:
            TracerUtils.logger.debug(f'pid: {pid} attachability check failed')
            return False
        
    @staticmethod
    def launch_tracer(is_pid: bool, command: str) -> None:
        tracer_handler = TracerHandler(is_pid, command)

        Frontend(
            title=f'Tracer PID {tracer_handler.pid}',
            pages_module_name='interceptor_window',
            default_page_name='Interceptor',
            toolbar_pages_order=['Interceptor', 'Help'],
            tracer_handler=tracer_handler
        )
