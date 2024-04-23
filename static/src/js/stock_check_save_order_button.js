odoo.define("button_save_stock_check_order.tree_button", function (require) {
    "use strict";
    var ListController = require("web.ListController");
    var ListView = require("web.ListView");
    var viewRegistry = require("web.view_registry");
    var AbstractController = require("web.AbstractController");

    var TreeButton = ListController.extend({
        buttons_template: "button_save_stock_check_order.buttons",
        events: _.extend({}, ListController.prototype.events, {
            "click .save_check_order_detail_action": "_SaveOrderCheckDetail"
        }),
        _SaveOrderCheckDetail: function () {
            var self = this;
            console.log(this.model.loadParams.context.active_id)
            console.log(this.model.loadParams.context)
            var quant_to_update = this.model.loadParams.context.quant_to_update
            self._rpc({
                model: 'stock.check.order',
                method: "save_check_order_detail",
                args:[this.model.loadParams.context.active_id,quant_to_update]
            });
        }
    });

    var SaleOrderListView = ListView.extend({
        config: _.extend({}, ListView.prototype.config, {
            Controller: TreeButton,
        }),
    });

    AbstractController.include({
        init() {
            this._super.apply(this, arguments);
        },

        _onOpenRecord: function (ev) {
            if (this?.initialState?.context?.autonsi_sale_plan_custom_row_click) {
                ev.stopPropagation();
                var record = this.model.get(ev.data.id, {
                    raw: true,
                });

                this.do_action({
                    type: "ir.actions.act_window",
                    name: "Open Sale Order Form View",
                    res_model: "sale.order",
                    res_id: record.data.order_id,
                    views: [[false, "form"]],
                });
                return;
            }

            this._super.apply(this, arguments);
        },
    });
    viewRegistry.add("button_save_stock_check_order", SaleOrderListView);
});
