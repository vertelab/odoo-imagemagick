var website = openerp.website;
var img_src = ''; // img src
var current_taget = null;

website.snippet.options.transform = website.snippet.Option.extend({
    start: function () {
        var self = this;
        this._super();
        current_taget = self.$target;

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
    },
    resetTransfo: function () {
        var self = this;
        this.$target.transfo("destroy");
        img_src = this.$target[0]["src"];
        //~ if (!~src.indexOf("/website/static/src/")) {
            //~ if (~src.indexOf("/ir.attachment/")) {
                //~ attachment_id = src.match(/ir.attachment\/(.*?)\//i)[1].split("_")[0];
            //~ }
        //~ }
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
                return  ($li.data('value') && self.$target.hasClass($li.data('value')));
            })
            .first()
            .addClass("active");
        this.$el.find('li:has(li[data-value].active)').addClass("active");
    },
    select: function (np) {
        var self = this;
        // add or remove html class
        if (np.$prev && this.required) {
            this.$target.removeClass(np.$prev.data('value' || ""));
        }
        if (np.$next) {
            if (np.$next.hasClass("choose_recipe")) {
                openerp.jsonRpc("/website_imagemagick_snippet_options", "call", {
                    "img_src": img_src,
                    "recipe_id": np.$next.data('value')
                }).done(function(data){
                    current_taget.attr("data-cke-saved-src", data);
                    current_taget.attr("src", data);
                });
            }
            else {
                this.$target.addClass(np.$next.data('value') || "");
            }
        }
    }
});

