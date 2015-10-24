# Simple Base Rig

Sometimes (especially with game engines) you cannot use complicated autorigging systems. But those systems have great tools that come with them. The compromise is to create a lesser rig attached to the more complicated one. Then skin that rig to the model instead. This script helps with that.

To install, throw this folder into your scripts directory.

To run, add a shelf icon with the text:

    import SimpleBaseRig as sb
    sb.Main()

Next build the Skeleton you want to use across all characters. The size doesn't matter, but make sure the heirarchy and joint names are what you want.

Click "Build Skeleton" to create a skeleton file from your Skeleton.

Open a file with the advanced rig in place and click "Retarget Skeleton". Work your way around the advanced rig selecting and clicking the appropriate buttons to target the rig. Save the file.

Click "Attach Skeleton" to place the skeleton on the rig.
