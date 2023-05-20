"use strict";
var __extends = (this && this.__extends) || (function () {
    var extendStatics = function (d, b) {
        extendStatics = Object.setPrototypeOf ||
            ({ __proto__: [] } instanceof Array && function (d, b) { d.__proto__ = b; }) ||
            function (d, b) { for (var p in b) if (b.hasOwnProperty(p)) d[p] = b[p]; };
        return extendStatics(d, b);
    };
    return function (d, b) {
        extendStatics(d, b);
        function __() { this.constructor = d; }
        d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
    };
})();
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
var node_1 = __importDefault(require("./node"));
var type_1 = __importDefault(require("./type"));
var CommentNode = /** @class */ (function (_super) {
    __extends(CommentNode, _super);
    function CommentNode(value) {
        var _this = _super.call(this) || this;
        /**
         * Node Type declaration.
         * @type {Number}
         */
        _this.nodeType = type_1.default.COMMENT_NODE;
        _this.rawText = value;
        return _this;
    }
    Object.defineProperty(CommentNode.prototype, "text", {
        /**
         * Get unescaped text value of current node and its children.
         * @return {string} text content
         */
        get: function () {
            return this.rawText;
        },
        enumerable: true,
        configurable: true
    });
    CommentNode.prototype.toString = function () {
        return "<!--" + this.rawText + "-->";
    };
    return CommentNode;
}(node_1.default));
exports.default = CommentNode;
