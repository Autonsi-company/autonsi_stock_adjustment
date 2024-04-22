odoo.define("button_create_stock_check_order.tree_button", function (require) {
  "use strict";
  var ListController = require("web.ListController");
  var ListView = require("web.ListView");
  var viewRegistry = require("web.view_registry");
  var AbstractController = require("web.AbstractController");

  var TreeButton = ListController.extend({
    buttons_template: "button_create_stock_check_order.buttons",
    events: _.extend({}, ListController.prototype.events, {
      "click .open_wizard_action": "_OpenWizard",
    }),
    _OpenWizard: function () {
      var self = this;

      this.do_action({
        type: "ir.actions.act_window",
        res_model: "stock.adjustment.order",

        view_mode: "form",
        view_type: "form",
        views: [[false, "form"]],
        target: "current",
        res_id: false
      });
    },
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
  viewRegistry.add("button_create_stock_check_order", SaleOrderListView);
});
