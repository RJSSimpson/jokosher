#
#    THIS FILE IS PART OF THE JOKOSHER PROJECT AND LICENSED UNDER THE GPL. SEE
#    THE 'COPYING' FILE FOR DETAILS
#
#    EffectWidget.py
#    
#    This module us used to create the custom Cairo widget that is used to
#    represent an effect.
#
#-------------------------------------------------------------------------------

import gtk
import math
import cairo
import gobject
import string


class EffectWidget(gtk.DrawingArea):
    """
        This class creates a custom Cairo widget that is displayed in the
        effects dialog box. This widget has the following actions:
        
            single click - move the widget order (not implemented yet)
            double click - show effect settings
            single click small red circle - remove the effect
    """
    
    def __init__(self, effectsdialog, effectname, effectnum):
        """Constructor for the class"""
        
        gtk.DrawingArea.__init__(self)
        self.BACKGROUND_RGB = (1, 1, 1)
        self.TEXT_RGB = (0, 0, 0)
        
        # the full name of the effect (such as 'Simple Delay 5s')
        self.effectname = effectname
        
        # a reference to the effects dialog
        self.effectsdialog = effectsdialog
        
        # the number of the effect in the chain. first is 0, second is 1 etc
        self.effectnum = effectnum

        # the size of the widget. hard coded right now
        # FIXME - make this not hard coded
        self.set_size_request(150, 80)

        # these are the events that the widget listens out for. used for
        # expose and click events
        self.set_events(gtk.gdk.POINTER_MOTION_MASK | gtk.gdk.BUTTON_RELEASE_MASK | gtk.gdk.BUTTON_PRESS_MASK | gtk.gdk.LEAVE_NOTIFY_MASK)

        # initialise the DrawingArea
        gtk.DrawingArea.__init__(self)
        
        # make signal connections. expose_event is important - whenever the
        # window exposes, the widget is re-drawn
        self.connect("expose_event", self.expose)
        self.connect("button_press_event", self.OnMouseDown)

    def expose(self, widget, event):
        """
            When the widget exposes, this method is called. It then triggers
            a redraw
        """
        
        # this is the context (the area to be drawn on) where we draw the
        # widget
        self.context = widget.window.cairo_create()
        
        # set a clip region for the expose event
        self.context.rectangle(event.area.x, event.area.y,
                               event.area.width, event.area.height)
        self.context.clip()
        
        # run draw() in this class to draw the widget
        self.draw(self.context)
        
        return False
    
    def draw(self, context):
        """Redraws the widget"""
        
        # grab a reference to the drawing area
        alloc = self.get_allocation()
        
        # set some variables
        x0 = 10 # top left hand x
        y0 = 10 # top left hand y
        rect_width = alloc.width - 15 # width of the widget
        rect_height = alloc.height - 15 # height of the widget
        radius = 50 # curvature of the widget corners
        
        # width and height of the context
        self.contextwidth = alloc.width
        self.contextheight = alloc.height
        
        x1 = 0
        y1 = 0
        
        x1=x0+rect_width;
        y1=y0+rect_height;
        
        if not rect_width or not rect_height:
            return
        
        # draw the widget
        if (rect_width / 2) < radius:
            if (rect_height / 2) <radius:
                self.context.move_to  (x0, (y0 + y1)/2)
                self.context.curve_to (x0 ,y0, x0, y0, (x0 + x1)/2, y0)
                self.context.curve_to (x1, y0, x1, y0, x1, (y0 + y1)/2)
                self.context.curve_to (x1, y1, x1, y1, (x1 + x0)/2, y1)
                self.context.curve_to (x0, y1, x0, y1, x0, (y0 + y1)/2)
            else:
                self.context.move_to  (x0, y0 + radius)
                self.context.curve_to (x0 ,y0, x0, y0, (x0 + x1)/2, y0)
                self.context.curve_to (x1, y0, x1, y0, x1, y0 + radius)
                self.context.line_to (x1 , y1 - radius)
                self.context.curve_to (x1, y1, x1, y1, (x1 + x0)/2, y1)
                self.context.curve_to (x0, y1, x0, y1, x0, y1- radius)
        else:
            if (rect_height/2) < radius:
                self.context.move_to  (x0, (y0 + y1)/2)
                self.context.curve_to (x0 , y0, x0 , y0, x0 + radius, y0)
                self.context.line_to (x1 - radius, y0)
                self.context.curve_to (x1, y0, x1, y0, x1, (y0 + y1)/2)
                self.context.curve_to (x1, y1, x1, y1, x1 - radius, y1)
                self.context.line_to (x0 + radius, y1)
                self.context.curve_to (x0, y1, x0, y1, x0, (y0 + y1)/2)
            else:
                self.context.move_to  (x0, y0 + radius)
                self.context.curve_to (x0 , y0, x0 , y0, x0 + radius, y0)
                self.context.line_to (x1 - radius, y0)
                self.context.curve_to (x1, y0, x1, y0, x1, y0 + radius)
                self.context.line_to (x1 , y1 - radius)
                self.context.curve_to (x1, y1, x1, y1, x1 - radius, y1)
                self.context.line_to (x0 + radius, y1)
                self.context.curve_to (x0, y1, x0, y1, x0, y1- radius)

        self.context.close_path()
        
        # create the gradient fill colour ranges
        gradient = cairo.LinearGradient(0.0, 0.0, 0, 100)
        gradient.add_color_stop_rgba(0.2, 252./255, 174./255, 62./255, 1)
        gradient.add_color_stop_rgba(1, 244./255, 120./255, 0./255, 0.5)
        
        # set the source as the gradient
        context.set_source(gradient)
        
        # fill the context with the gradient
        context.fill_preserve()
        
        # set the border colour for the widget
        self.context.set_source_rgba (173, 73, 0, 0.5);
        
        # draw it
        self.context.stroke()
        
        # call formatEffectText() to split the text into different lines to
        # fit inside the widget
        effecttext = self.formatEffectText(self.effectname)
        
        # grab the length of the effecttext list (this returns the number of
        # rows of text)
        labellen = len(effecttext)
        
        # set the source colour to black for the text
        self.context.set_source_rgb(0, 0, 0)
        
        # set the font size
        self.context.set_font_size(12)
        
        # set the text height
        textheight = self.contextheight / 2
        
        # for each line of line of text, move to the middle of the widget
        # and move back the number of letters in the line. then draw the
        # text and stroke it
        for line in effecttext:            
            self.context.move_to((self.contextwidth / 2) - (len(line) * 3), textheight)
            self.context.show_text(line)
            self.context.stroke();
            textheight += 12
            
            x = alloc.x + alloc.width / 2
            y = alloc.y + alloc.height / 2
            
            radius = min(alloc.width / 5, alloc.height / 5) - 5
        
        # draw the delete button
        self.context.arc(alloc.width - (radius + 2), radius + 2, radius, 0, 2 * math.pi)
        self.context.set_source_rgb(2, 0, 0)
        self.context.fill_preserve()
        self.context.set_source_rgb(0, 0, 0)
        self.context.stroke_preserve()
        
    def OnMouseDown(self, widget, mouse):
        """
            If the mouse is clicked, detect where it is clicked and whether
            it is a double click or not.
        """
        
        if self.context.in_fill(mouse.x, mouse.y):
            self.effectsdialog.OnRemoveEffect(self, self.effectnum)
        else:
            if mouse.type == gtk.gdk._2BUTTON_PRESS:
                self.effectsdialog.OnEffectSetting(self)
            else:
                # effect moving happens here, but its not in yet
                pass

    def formatEffectText(self, text):
        """
            This method takes 'text' and splits it into a bunch of different
            lines, each one being in a list element. We can then iterate
            through the list to add the text in the widget.
        """
        
        words = string.split(text)
        
        finallist = []
        linetext = ""
        
        # the maximum length of a line
        linelength = 20
        remainder = linelength
        
        for w in words:
            wordlength = len(w)
            
            if wordlength <= remainder:
                remainder -= wordlength + 1
                linetext = linetext + w + " "
            else:
                finallist.append(linetext)
                linetext = ""
                linetext = linetext + w + " "
                remainder = 20 - len(linetext)

        finallist.append(linetext)
        return finallist