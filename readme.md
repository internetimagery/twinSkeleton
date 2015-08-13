# Simple Base Rig

Sometimes (especially with game engines) you cannot use complicated autorigging systems. But those systems have great tools that come with them. The compromise is to create a lesser rig attached to the more complicated one. Then skin that rig to the model instead. This script helps with that.

To install, throw this folder into your scripts directory.

To run, add a shelf icon with the text:

    import SimpleBaseRig as sb
    sb.Main()

To use, first build a template. Selecting joints on your advanced rig in the viewport, and selecting the corresponding button. After you're done, save the file somewhere.

Now you can create a smaller base rig whenever you want on the more complicated one by loading that template file.
