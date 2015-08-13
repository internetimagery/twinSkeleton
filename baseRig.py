# The base rig structure
from os.path import join

rig = {
    "root" : {
        "spine_pelvis" : {
            "spine_middle" : {
                "spine_lower_ribcage" : {
                    "spine_neck_base" : {
                        "spine_skull_base" : {
                            "spine_skull_top" : {}
                        }
                    }
                }
            }
            "left_leg_hip" : {
                "left_leg_knee" : {
                    "left_leg_ankle" : {
                        "left_leg_foot_heel" : {
                            "left_leg_foot_ball" : {
                                "left_leg_foot_toe" : {}
                            }
                        }
                    }
                }
            }
            "right_leg_hip" : {
                "right_leg_knee" : {
                    "right_leg_ankle" : {
                        "right_leg_foot_heel" : {
                            "right_leg_foot_ball" : {
                                "right_leg_foot_toe" : {}
                            }
                        }
                    }
                }
            }
        }
    }
}
