import os
from pathlib import Path
from open3d.ml.tf.pipelines import SemanticSegmentation
from open3d.ml.tf.models import RandLANet, KPFCNN

kpconv_url = "https://storage.googleapis.com/open3d-releases/model-zoo/kpconv_semantickitti_202009090354utc.pth"
randlanet_url = "https://storage.googleapis.com/open3d-releases/model-zoo/randlanet_semantickitti_202009090354utc.pth"

ckpt_path = "./logs/vis_weights_{}.pth".format('RandLANet')
if not Path(ckpt_path).exists():
    cmd = "wget {} -O {}".format(randlanet_url, ckpt_path)
    os.system(cmd)
model = RandLANet(ckpt_path=ckpt_path)
pipeline_r = SemanticSegmentation(model)
pipeline_r.load_ckpt(model.cfg.ckpt_path)

ckpt_path = "./logs/vis_weights_{}.pth".format('KPFCNN')
if not Path(ckpt_path).exists():
    cmd = "wget {} -O {}".format(kpconv_url, ckpt_path)
    print(cmd)
    os.system(cmd)
model = KPFCNN(ckpt_path=ckpt_path, in_radius=10)
pipeline_k = SemanticSegmentation(model)
pipeline_k.load_ckpt(model.cfg.ckpt_path)

data_path = os.path.dirname(os.path.realpath(__file__)) + "/demo_data"
pc_names = ["000700", "000750"]

# see this function in examples/vis_pred.py,
# or it can be your customized dataloader,
# or you can use the exsisting get_data() methods in ml3d/datasets
pcs = get_custom_data(pc_names, data_path)