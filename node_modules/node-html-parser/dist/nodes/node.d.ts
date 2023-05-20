import NodeType from './type';
/**
 * Node Class as base class for TextNode and HTMLElement.
 */
export default abstract class Node {
    nodeType: NodeType;
    childNodes: Node[];
    text: string;
    rawText: string;
    abstract toString(): string;
}
