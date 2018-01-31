var website = openerp.website;

website.snippet.options.transform = website.snippet.Option.extend({
    start: function () {
        var self = this;
        this._super();

        this.$el.find(".clear-style").click(function (event) {
            self.$target.removeClass("fa-spin").attr("style", "");
            self.resetTransfo();
        });

        this.$el.find(".style").click(function (event) {
            var settings = self.$target.data("transfo").settings;
            self.$target.transfo({ hide: (settings.hide = !settings.hide) });
        });

        this.$overlay.find('.oe_snippet_clone, .oe_handles').addClass('hidden');

        this.$overlay.find('[data-toggle="dropdown"]')
            .on("mousedown", function () {
                self.$target.transfo("hide");
            });

        //~ $(".choose_recipe").click(function(){
        //~ console.log($(this));
        //~ openerp.jsonRpc("/website_imagemagick_snippet_options", "call", {
        //~ }).done(function(data){
            //~ var blog_content = '';
            //~ i = 0;
            //~ $.each(data, function(key, info) {
                //~ var content = openerp.qweb.render('blog_banner_content', {
                    //~ 'item_content': i == 0 ? "item active" : "item",
                    //~ 'blog_name': data[key]['name'],
                    //~ 'background_image': data[key]['background_image'],
                //~ });
                //~ blog_content += content;
                //~ i ++;
            //~ });
            //~ self.$target.find(".blog_banner_content").html(blog_content);
        //~ });
    //~ });

    },
    resetTransfo: function () {
        var self = this;
        this.$target.transfo("destroy");
        var src = this.$target[0]["src"];
        if (!~src.indexOf("/website/static/src/")) {
            if (~src.indexOf("/ir.attachment/")) {
                console.log(src.match(/ir.attachment\/(.*?)\//i)[1].split("_")[0]);
            }
        }
        this.$target.transfo({
            hide: true,
            callback: function () {
                var center = $(this).data("transfo").$markup.find('.transfo-scaler-mc').offset();
                var $option = self.$overlay.find('.btn-group:first');
                self.$overlay.css({
                    'top': center.top - $option.height()/2,
                    'left': center.left,
                    'position': 'absolute',
                });
                self.$overlay.find(".oe_overlay_options").attr("style", "width:0; left:0!important; top:0;");
                self.$overlay.find(".oe_overlay_options > .btn-group").attr("style", "width:160px; left:-80px;");
            }});
        this.$target.data('transfo').$markup
            .on("mouseover", function () {
                self.$target.trigger("mouseover");
            })
            .mouseover();
    },
    onFocus : function () {
        this.resetTransfo();
    },
    onBlur : function () {
        this.$target.transfo("hide");
    },
    set_active: function () {
        var self = this;
        this.$el.find('li').removeClass("active");
        var $active = this.$el.find('li[data-value]')
            .filter(function () {
                var $li = $(this);
                console.log($li);
                return  ($li.data('value') && self.$target.hasClass($li.data('value')));
            })
            .first()
            .addClass("active");
        this.$el.find('li:has(li[data-value].active)').addClass("active");
    },
    select: function (np) {
        var self = this;
        console.log(self);
        // add or remove html class
        if (np.$prev && this.required) {
            this.$target.removeClass(np.$prev.data('value' || ""));
        }
        if (np.$next) {
            this.$target.addClass(np.$next.data('value') || "");
        }
    }
});

