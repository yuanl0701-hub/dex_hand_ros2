#!/usr/bin/env python3
"""Load a dexterous-hand asset and connect it to ROS 2 in Isaac Sim 4.5.

Run this file with Isaac Sim's ``python.sh`` rather than the system Python.
Only standard ROS ``sensor_msgs/JointState`` messages cross into Isaac Sim;
the project's custom gesture interfaces remain in the external ROS 2 node.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


REVO2_ACTIVE_JOINTS = (
    "right_index_proximal_joint",
    "right_ring_proximal_joint",
    "right_middle_proximal_joint",
    "right_pinky_proximal_joint",
    "right_thumb_metacarpal_joint",
    "right_thumb_proximal_joint",
)
REVO2_MIMIC_JOINTS = (
    "right_index_distal_joint",
    "right_ring_distal_joint",
    "right_middle_distal_joint",
    "right_pinky_distal_joint",
    "right_thumb_distal_joint",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    asset = parser.add_mutually_exclusive_group(required=True)
    asset.add_argument("--urdf", help="Expanded URDF file")
    asset.add_argument(
        "--usd",
        help="Existing articulated USD, including the Revo2 right-hand asset",
    )
    parser.add_argument(
        "--usd-root-path",
        default="/World/Revo2",
        help="Stage prim receiving the referenced USD default prim",
    )
    parser.add_argument(
        "--articulation-path",
        default="",
        help="Articulation-root prim; inferred for the supported Revo2 asset",
    )
    parser.add_argument(
        "--command-topic",
        default="/dex_hand/joint_command",
        help="JointState position-command topic consumed by Isaac Sim",
    )
    parser.add_argument(
        "--state-topic",
        default="/isaac_joint_states",
        help="JointState topic published from the Isaac Sim articulation",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run without the Isaac Sim viewport",
    )
    parser.add_argument(
        "--drive-stiffness",
        type=float,
        default=120.0,
        help="Imported position-drive stiffness",
    )
    parser.add_argument(
        "--drive-damping",
        type=float,
        default=8.0,
        help="Imported position-drive damping",
    )
    parser.add_argument(
        "--height",
        type=float,
        default=0.06,
        help="Height of the fixed palm above the ground plane in metres",
    )
    parser.add_argument(
        "--save-stage",
        default="",
        help="Optional USD path to export after setup",
    )
    return parser.parse_args()


ARGS = parse_args()

from isaacsim import SimulationApp  # noqa: E402


SIMULATION_APP = SimulationApp(
    {
        "headless": ARGS.headless,
        "width": 1280,
        "height": 720,
    }
)


def main() -> int:
    from isaacsim.core.api import World
    from isaacsim.core.utils.extensions import enable_extension
    from isaacsim.core.utils.stage import add_reference_to_stage
    from isaacsim.core.utils.viewports import set_camera_view
    import omni.graph.core as og
    import omni.kit.commands
    import omni.usd
    from pxr import Gf, UsdGeom, UsdLux

    if ARGS.drive_stiffness <= 0 or ARGS.drive_damping < 0:
        raise ValueError("drive stiffness must be positive and damping non-negative")

    enable_extension("isaacsim.ros2.bridge")
    if ARGS.urdf:
        enable_extension("isaacsim.asset.importer.urdf")
    for _ in range(5):
        SIMULATION_APP.update()

    omni.usd.get_context().new_stage()
    world = World(stage_units_in_meters=1.0)
    world.scene.add_default_ground_plane()

    stage = omni.usd.get_context().get_stage()
    light = UsdLux.DistantLight.Define(stage, "/World/KeyLight")
    light.CreateIntensityAttr(2500.0)
    UsdGeom.Xformable(light.GetPrim()).AddRotateXYZOp().Set(
        Gf.Vec3f(-35.0, 25.0, 20.0)
    )

    if ARGS.urdf:
        from isaacsim.asset.importer.urdf import _urdf

        urdf_path = Path(ARGS.urdf).expanduser().resolve()
        if not urdf_path.is_file():
            raise FileNotFoundError(f"URDF does not exist: {urdf_path}")

        import_config = _urdf.ImportConfig()
        import_config.convex_decomp = False
        import_config.fix_base = True
        import_config.make_default_prim = True
        import_config.self_collision = False
        import_config.distance_scale = 1.0
        import_config.density = 0.0

        parsed, robot_model = omni.kit.commands.execute(
            "URDFParseFile",
            urdf_path=str(urdf_path),
            import_config=import_config,
        )
        if not parsed:
            raise RuntimeError(f"Isaac Sim failed to parse URDF: {urdf_path}")

        for joint_name in robot_model.joints:
            drive = robot_model.joints[joint_name].drive
            drive.strength = float(ARGS.drive_stiffness)
            drive.damping = float(ARGS.drive_damping)

        imported, prim_path = omni.kit.commands.execute(
            "URDFImportRobot",
            urdf_robot=robot_model,
            import_config=import_config,
        )
        if not imported or not prim_path:
            raise RuntimeError("Isaac Sim failed to import the hand articulation")
        transform_prim_path = prim_path
        asset_description = str(urdf_path)
        controlled_joints = tuple(f"motor_{index}_joint" for index in range(1, 7))
    else:
        usd_path = Path(ARGS.usd).expanduser().resolve()
        if not usd_path.is_file():
            raise FileNotFoundError(f"USD does not exist: {usd_path}")
        if not ARGS.usd_root_path.startswith("/"):
            raise ValueError("--usd-root-path must be an absolute USD prim path")

        add_reference_to_stage(
            usd_path=str(usd_path),
            prim_path=ARGS.usd_root_path,
        )
        for _ in range(5):
            SIMULATION_APP.update()

        prim_path = (
            ARGS.articulation_path
            or f"{ARGS.usd_root_path.rstrip('/')}/root_joint"
        )
        transform_prim_path = ARGS.usd_root_path
        asset_description = str(usd_path)
        controlled_joints = REVO2_ACTIVE_JOINTS

        joints_path = f"{ARGS.usd_root_path.rstrip('/')}/joints"
        missing_joints = [
            name
            for name in REVO2_ACTIVE_JOINTS + REVO2_MIMIC_JOINTS
            if not stage.GetPrimAtPath(f"{joints_path}/{name}").IsValid()
        ]
        if missing_joints:
            raise RuntimeError(
                "USD is not the supported 6-active/5-mimic Revo2 right hand; "
                f"missing joints: {', '.join(missing_joints)}"
            )

    robot_prim = stage.GetPrimAtPath(prim_path)
    if not robot_prim.IsValid():
        raise RuntimeError(f"imported articulation prim is invalid: {prim_path}")
    transform_prim = stage.GetPrimAtPath(transform_prim_path)
    if not transform_prim.IsValid():
        raise RuntimeError(f"model transform prim is invalid: {transform_prim_path}")
    UsdGeom.XformCommonAPI(transform_prim).SetTranslate(
        Gf.Vec3d(0.0, 0.0, float(ARGS.height))
    )

    og.Controller.edit(
        {"graph_path": "/DexHandActionGraph", "evaluator_name": "execution"},
        {
            og.Controller.Keys.CREATE_NODES: [
                ("OnPlaybackTick", "omni.graph.action.OnPlaybackTick"),
                (
                    "SubscribeJointState",
                    "isaacsim.ros2.bridge.ROS2SubscribeJointState",
                ),
                (
                    "PublishJointState",
                    "isaacsim.ros2.bridge.ROS2PublishJointState",
                ),
                (
                    "ArticulationController",
                    "isaacsim.core.nodes.IsaacArticulationController",
                ),
                ("ReadSimTime", "isaacsim.core.nodes.IsaacReadSimulationTime"),
            ],
            og.Controller.Keys.CONNECT: [
                (
                    "OnPlaybackTick.outputs:tick",
                    "SubscribeJointState.inputs:execIn",
                ),
                (
                    "OnPlaybackTick.outputs:tick",
                    "PublishJointState.inputs:execIn",
                ),
                (
                    "OnPlaybackTick.outputs:tick",
                    "ArticulationController.inputs:execIn",
                ),
                (
                    "ReadSimTime.outputs:simulationTime",
                    "PublishJointState.inputs:timeStamp",
                ),
                (
                    "SubscribeJointState.outputs:jointNames",
                    "ArticulationController.inputs:jointNames",
                ),
                (
                    "SubscribeJointState.outputs:positionCommand",
                    "ArticulationController.inputs:positionCommand",
                ),
                (
                    "SubscribeJointState.outputs:velocityCommand",
                    "ArticulationController.inputs:velocityCommand",
                ),
                (
                    "SubscribeJointState.outputs:effortCommand",
                    "ArticulationController.inputs:effortCommand",
                ),
            ],
            og.Controller.Keys.SET_VALUES: [
                (
                    "SubscribeJointState.inputs:topicName",
                    ARGS.command_topic,
                ),
                (
                    "PublishJointState.inputs:topicName",
                    ARGS.state_topic,
                ),
                (
                    "ArticulationController.inputs:robotPath",
                    prim_path,
                ),
                (
                    "PublishJointState.inputs:targetPrim",
                    prim_path,
                ),
            ],
        },
    )

    if ARGS.save_stage:
        save_path = Path(ARGS.save_stage).expanduser().resolve()
        save_path.parent.mkdir(parents=True, exist_ok=True)
        if not stage.GetRootLayer().Export(str(save_path)):
            raise RuntimeError(f"failed to export USD stage: {save_path}")
        print(f"Saved Isaac Sim stage: {save_path}", flush=True)

    set_camera_view(
        eye=[0.26, 0.24, 0.20],
        target=[0.04, 0.0, 0.06],
        camera_prim_path="/OmniverseKit_Persp",
    )

    world.reset()
    world.play()
    print(
        "DEX hand loaded in Isaac Sim\n"
        f"  asset: {asset_description}\n"
        f"  articulation: {prim_path}\n"
        f"  controlled joints: {', '.join(controlled_joints)}\n"
        f"  command topic: {ARGS.command_topic}\n"
        f"  state topic: {ARGS.state_topic}\n"
        "Keep the timeline playing, then publish a gesture from ROS 2.",
        flush=True,
    )

    while SIMULATION_APP.is_running():
        world.step(render=not ARGS.headless)
    return 0


if __name__ == "__main__":
    exit_code = 1
    try:
        exit_code = main()
    except Exception as exc:
        print(f"Isaac Sim dex-hand startup failed: {exc}", file=sys.stderr)
    finally:
        SIMULATION_APP.close()
    raise SystemExit(exit_code)
