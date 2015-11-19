# Twin Skeleton

Twin Skeleton is a tool to quickly, simply and consistently build a skeleton and attach it to some predefined points. This can be used if you happen to have consistently named control objects (position them and then let the tool build the skeleton), but it is most useful in games.

Sometimes (especially with game engines) you cannot use complicated autorigging systems. But those systems have great tools that come with them, GUI pickers etc. The compromise is to create a lesser Twin Skeleton attached to the more complicated one, sometimes with less joints than the complicated one too (such as omitting twist joints). Then skin that Twin Skeleton to the model instead.

This script facilitates that.

### Installation

To install, [download the "install.mel"](https://github.com/internetimagery/twinSkeleton/releases/latest) file and drag/drop it into Maya.
Or else download this folder. Unzip and name it "twinSkeleton". Throw it into your scripts directory.

To run, add a shelf icon with the text:

    import twinSkeleton as twin
    twin.Main()

### Three Step Process

Creating the skeleton is a three step process, of which all steps are reusable.

#### Step one

Manually create the Skeleton you want to reuse across all characters. The size and joint position don't matter, but make sure the hierarchy and joint names are what you want. Take the time to get it right here!

Click "Build Skeleton" to create a skeleton file and save it somewhere.

#### Step Two

Open a file with the advanced rig that you want to attach your Twin Skeleton to. Run the tool and click "Retarget Skeleton".
Work your way around the advanced rig selecting and clicking the appropriate buttons to target the rig.
You can click Position, Rotation, Scale to set them individually or simply click the joint name to attach all three.
Note: The rotation order determines the axis that aims down the joint too.

Save the file. The file contains all the skeletons info as well as attachment information too, so you can save over the previous file if you like. If you have a new rig to attach your Twin Skeleton to, reload this file, retarget and save a new copy.

#### Step Three

With your scene containing the advanced rig open, load the tool a third and final time.
Click "Attach Skeleton" to place the skeleton on the rig.

The following options are important.

##### Orient Junctions ::

When picking joint rotation angles, limbs are straight forward. Point one joint at another. But when it comes to multi-joint junctions such as the hips or the hand it's not as clear.
With the option turned on, joints will be pointed at the furthest joint in the group.
With the option off, the joint will face worldspace.

Experiment with what works for your rig, but remember to keep it consistent.

##### Prevent Flipping ::

With this option on it will keep rotations around an entire limb the same.
ie: positive angles will turn the joint the same direction. This makes it easier to directly manipulate joints.
Use this if you are planning on animating the joints directly or you need consistent rotation information.
With this off, joints will orient consistently to the angles presented on an individual bases.
Generally you would want to keep this option off if you're not manually touching the Twin Skeleton.

##### Display Axis ::

With this option on, all rotational axis will be displayed. You may have noticed all of these options are to do with rotation. It is vital you get your rotations relatively consistent between rigs. So it's highly recommended that you turn this on to get a sense of what the joints are doing and to correct anything if need be.
