"""
Binary Tree, Stack Data Structure
Code borrowed from Runestone Academy
https://runestone.academy/runestone/books/index
"""


class BinaryTree:
    """
    Binary Tree Data Structure
    Code borrowed from Runestone Academy
    https://runestone.academy/runestone/books/index
    """

    def __init__(self, rootObj):
        self.key = rootObj
        self.leftChild = None
        self.rightChild = None

    def insertLeft(self, newNode):
        # print('call to insert left')
        if self.leftChild == None:
            self.leftChild = BinaryTree(newNode)
        else:
            t = BinaryTree(newNode)
            t.leftChild = self.leftChild
            self.leftChild = t

    def insertRight(self, newNode):
        if self.rightChild == None:
            self.rightChild = BinaryTree(newNode)
        else:
            t = BinaryTree(newNode)
            t.rightChild = self.rightChild
            self.rightChild = t

    def insertLeftTree(self, newTree):
        if self.leftChild == None:
            self.leftChild = newTree
        else:
            print('Left tree already present')

    def getRightChild(self):
        return self.rightChild

    def getLeftChild(self):
        return self.leftChild

    def setRootVal(self, obj):
        self.key = obj

    def getRootVal(self):
        return self.key

    def getChildren(self):
        return [self.leftChild(), self.rightChild()]


    # def get_leaf_nodes(self):
    #     leafs = []
    #     self._collect_leaf_nodes(self, leafs)
    #     return leafs
    #
    # def _collect_leaf_nodes(self, node, leafs):
    #     print(node)
    #     if node is not None:
    #         if len(node.getChildren()) == 0:
    #             leafs.append(node)
    #         for n in node.getChildren():
    #             self._collect_leaf_nodes(n, leafs)


class Stack:
    """
    Stack Data Structure
    Code borrowed from Runestone Academy
    https://runestone.academy/runestone/books/index
    """

    def __init__(self):
        self.items = []

    def isEmpty(self):
        return self.items == []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        return self.items.pop()

    def peek(self):
        return self.items[len(self.items) - 1]

    def size(self):
        return len(self.items)


def buildParseTree(fpexp, operator_list=['+', '-', '*', '/', 'INSIDE', 'OR', 'or', 'NOT', 'AND', 'SIZE', 'BY']):
    """
    Code to build tree from expression
    Code borrowed from Runestone Academy
    https://runestone.academy/runestone/books/index
    """
    fplist = fpexp.split()
    pStack = Stack()
    eTree = BinaryTree('')
    pStack.push(eTree)
    currentTree = eTree

    for i in fplist:
        if i == '(':
            currentTree.insertLeft('')
            pStack.push(currentTree)
            currentTree = currentTree.getLeftChild()

        elif i in operator_list:
            currentTree.setRootVal(i)
            currentTree.insertRight('')
            pStack.push(currentTree)
            currentTree = currentTree.getRightChild()

        elif i == ')':
            currentTree = pStack.pop()

        elif i not in operator_list + [')']:
            try:
                currentTree.setRootVal(i)
                parent = pStack.pop()
                currentTree = parent

            except ValueError:
                raise ValueError("token '{}' is not a valid integer".format(i))

    return eTree
