# Twin Skeleton

Twin Skeleton is a tool to quickly, simply and consistently build a skeleton and attach it to some predefined points. This can be used if you happen to have consistently named control objects (position them and then let the tool build the skeleton), but it is most useful in games.

Sometimes (especially with game engines) you cannot use complicated autorigging systems. But those systems have great tools that come with them, GUI pickers etc. The compromise is to create a lesser Twin Rig attached to the more complicated one, sometimes with less joints than the complicated one too. Then skin that Twin Rig to the model instead. This script facilitates that.

To install, download the "install.mel" file and drag/drop it into Maya.
Or else download this folder. Unzip and name it "twinSkeleton". Throw it into your scripts directory.

To run, add a shelf icon with the text:

    import twinSkeleton as twin
    twin.Main()

Build the Skeleton you want to use across all characters. The size doesn't matter, but make sure the heirarchy and joint names are what you want.

Click "Build Skeleton" to create a skeleton file from your Skeleton.

Open a file with the advanced rig in place and click "Retarget Skeleton". Work your way around the advanced rig selecting and clicking the appropriate buttons to target the rig. Save the file.

Click "Attach Skeleton" to place the skeleton on the rig.
