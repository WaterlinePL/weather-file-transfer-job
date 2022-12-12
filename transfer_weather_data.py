import os.path
import sys

from hmse_job_utils.utils.img_simulation_utils import get_project_simulation_dir, read_local_project_metadata, \
    get_used_hydrus_models
from hmse_projects.hmse_hydrological_models.hydrus import hydrus_utils
from hmse_projects.hmse_hydrological_models.weather_data import weather_util
from hmse_projects.project_dao import ProjectDao

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <project name>")
        exit(1)

    project_id = sys.argv[1]
    sim_dir = get_project_simulation_dir(project_id)
    project_metadata = read_local_project_metadata(project_id)
    hydrus_models_to_process = [hydrus_id for hydrus_id in get_used_hydrus_models(project_metadata)
                                if hydrus_id in project_metadata["hydrus_to_weather"]]

    for hydrus_id in hydrus_models_to_process:
        weather_id = project_metadata["hydrus_to_weather"][hydrus_id]
        hydrus_path = os.path.join(sim_dir, 'hydrus', hydrus_id)
        hydrus_length_unit = hydrus_utils.get_hydrus_length_unit(hydrus_path)
        raw_data = weather_util.read_weather_csv(ProjectDao.get_weather_model_path(project_id, weather_id))
        ready_data = weather_util.adapt_data(raw_data, hydrus_length_unit)
        success = weather_util.add_weather_to_hydrus_model(hydrus_path, ready_data)
        if not success:
            raise RuntimeError(f"Weather transfer failed on weather file {weather_id} and hydrus model {hydrus_id}")
