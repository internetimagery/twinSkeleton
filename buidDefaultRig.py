# Build a default base rig structure file

rig = {
    "all_translate" : {
        "spine_pelvis" : {
            "spine_middle" : {
                "spine_lower_ribcage" : {
                    "spine_neck_base" : {
                        "spine_skull_base" : {
                            "spine_skull_top" : {}
                        },
                    },
                },
                "left_arm_scapula_base" : {
                    "left_arm_shoulder" : {
                        "left_arm_elbow" : {
                            "left_arm_wrist" : {
                                "left_arm_hand_thumb_base" : {
                                    "left_arm_hand_thumb_middle" : {
                                        "left_arm_hand_thumb_tip" : {}
                                    },
                                },
                                "left_arm_hand_indexFinger_knuckle" : {
                                    "left_arm_hand_indexFinger_upperjoint" : {
                                        "left_arm_hand_indexFinger_lowerjoint" : {
                                            "left_arm_hand_indexFinger_tip" : {}
                                        },
                                    },
                                },
                                "left_arm_hand_middleFinger_knuckle" : {
                                    "left_arm_hand_middleFinger_upperjoint" : {
                                        "left_arm_hand_middleFinger_lowerjoint" : {
                                            "left_arm_hand_middleFinger_tip" : {}
                                        },
                                    },
                                },
                                "left_arm_hand_ringFinger_knuckle" : {
                                    "left_arm_hand_ringFinger_upperjoint" : {
                                        "left_arm_hand_ringFinger_lowerjoint" : {
                                            "left_arm_hand_ringFinger_tip" : {}
                                        },
                                    },
                                },
                                "left_arm_hand_littleFinger_knuckle" : {
                                    "left_arm_hand_littleFinger_upperjoint" : {
                                        "left_arm_hand_littleFinger_lowerjoint" : {
                                            "left_arm_hand_littleFinger_tip" : {}
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
                "right_arm_scapula_base" : {
                    "right_arm_shoulder" : {
                        "right_arm_elbow" : {
                            "right_arm_wrist" : {
                                "right_arm_hand_thumb_base" : {
                                    "right_arm_hand_thumb_middle" : {
                                        "right_arm_hand_thumb_tip" : {}
                                    },
                                },
                                "right_arm_hand_indexFinger_knuckle" : {
                                    "right_arm_hand_indexFinger_upperjoint" : {
                                        "right_arm_hand_indexFinger_lowerjoint" : {
                                            "right_arm_hand_indexFinger_tip" : {}
                                        },
                                    },
                                },
                                "right_arm_hand_middleFinger_knuckle" : {
                                    "right_arm_hand_middleFinger_upperjoint" : {
                                        "right_arm_hand_middleFinger_lowerjoint" : {
                                            "right_arm_hand_middleFinger_tip" : {}
                                        },
                                    },
                                },
                                "right_arm_hand_ringFinger_knuckle" : {
                                    "right_arm_hand_ringFinger_upperjoint" : {
                                        "right_arm_hand_ringFinger_lowerjoint" : {
                                            "right_arm_hand_ringFinger_tip" : {}
                                        },
                                    },
                                },
                                "right_arm_hand_littleFinger_knuckle" : {
                                    "right_arm_hand_littleFinger_upperjoint" : {
                                        "right_arm_hand_littleFinger_lowerjoint" : {
                                            "right_arm_hand_littleFinger_tip" : {}
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            },
            "left_leg_hip" : {
                "left_leg_knee" : {
                    "left_leg_ankle" : {
                        "left_leg_foot_ball" : {
                            "left_leg_foot_toe" : {}
                        },
                    },
                },
            },
            "right_leg_hip" : {
                "right_leg_knee" : {
                    "right_leg_ankle" : {
                        "right_leg_foot_ball" : {
                            "right_leg_foot_toe" : {}
                        },
                    },
                },
            },
        },
    },
}

if __name__ == "__main__":
    import __main__
    from json import dump
    from sys import argv, exit
    from os import getcwd, path
    from argparse import ArgumentParser
    parser = ArgumentParser(description="Create a base rig file")
    parser.add_argument("file", help="The file in which to save this base")
    args = parser.parse_args()
    f = path.realpath(path.join(getcwd(), args.file))

    if path.exists(f):
        try:
            q = raw_input("File exists. Replace it? (Y|N): ")
        except NameError:
            q = input("File exists. Replace it? (Y|N): ")
        if "y" not in q.lower():
            exit("Canceled")
    with open(f, "w") as f:
        dump(rig, f, sort_keys=True, indent=4)
