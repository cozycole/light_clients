"""
Quinn Fetrow
02/10/2022

A dynamic Merkle Tree class and Node class to be used with any node values.  
Must be initialized before use with initialize(), used in blockchain.py to generate merkle roots
for each block, and fullnode.py to return a path to the lightclient.


"""

from hashlib import sha1
import math

class MerkleNode:
    def __init__(self, value, rightNode, leftNode, content):
        self.value = value # hashed 
        self.rightNode = rightNode
        self.leftNode = leftNode
        self.content = content # transaction information, only in leaf nodes
        self.parent = None

    def set_parent(self, parentNode):
        # sets a node parent, after tree is generated
        self.parent = parentNode

    def get_value(self):
        return self.value

class MerkleTree:
    """ 
    Represents the merkle tree, used in the block to generate the root, and the full node to generate a path

    A couple things to note:
        1. The tree hashes values as they come before initialization
        2. The user must call initialize() after all nodes are appended
        3. Hashing values together is done in a few steps:
                Step 1: Convert hash strings to integers
                Step 2: Combine using bitwise OR "|"
                Step 3: Convert back to string and hash
            This must be done this way because hash(1,2) must be the same as hash(2,1) for the proof
            to be accessible
        4. If a tree is odd, the last value is duplicated
        5. The tree is split to the largest 2^n<len(nodes)

        For example:
                                Root (Hash012344)
                             /                      \
                        Hash0123                  Hash44
                        /      \                 /      \
                    Hash01      Hash23         Hash4   Hash4  <---- Last value is duplicated and hashed
                    /   \        /   \             
                Hash0  Hash1  Hash2  Hash3     

    """
    def __init__(self):
        self.nodes = [] # holds all nodes
        self.root = None # head node
    
    def addNode(self, nodeValue):
        # adds a node to the list, NOT the tree
        hashedvalue = sha1(str(nodeValue).encode()).hexdigest()
        newnode = MerkleNode(hashedvalue, None, None, nodeValue)
        self.nodes.append(newnode)

    def initialize(self):
        # Once all nodes are appended, run initialize
        if len(self.nodes) % 2 == 1:
            self.nodes.append(self.nodes[(len(self.nodes)-1)])
        print("\tGenerating Merkle Tree...")
        self.root = self._generatetree(self.nodes)
        self._set_parents(self.root)
        if self.root:
            print("\tMerkle Tree Generated with root: {s}".format(s = self.root.get_value()))
    
    def _generatetree(self, nodeSubSection):
        # Recursive function that generates a merkle tree given a subsection of nodes
        # Starts with the full list of nodes, generating nodes top-down
        if len(nodeSubSection) == 0:
            # tree was initialized with no nodes
            return
        # split_id is the point to split the subsection
        split_id = len(nodeSubSection) - (2**int((math.log(len(nodeSubSection),2))//1))//2 # split into largest n division of 2^n
        if len(nodeSubSection) == 2:
            concatenated = int(nodeSubSection[0].get_value(),16) + int(nodeSubSection[1].get_value(),16)
            newhash = sha1(str(concatenated).encode()).hexdigest()
            newNode = MerkleNode(newhash, nodeSubSection[1], nodeSubSection[0], None)
            return newNode
        left = self._generatetree(nodeSubSection[:split_id]) # call recursively on left "half"
        right = self._generatetree(nodeSubSection[split_id:]) # call recursively on right "half"
        concatenated = str(int(left.get_value(),16) + int(right.get_value(),16))
        value = sha1(concatenated.encode()).hexdigest()
        return MerkleNode(value, right, left, None)

    def _set_parents(self, node):
    # recursive function to set the parent of all node
        if node != None:
            if node.leftNode != None:
                node.leftNode.set_parent(node)
                node.rightNode.set_parent(node)
                self._set_parents(node.leftNode)
                self._set_parents(node.rightNode)
        

    def print_tree(self):
        # For debugging only
        self._printRecursive(self.root)

    def _printRecursive(self, node):
        # Debugging only, prints the tree recursively
        if node != None:
            if node.parent != None:
                print("Parent: "+str(node.parent.get_value()))
            else:
                print("Root")
            if node.leftNode != None:
                print("Left: "+str(node.leftNode.content)+ ", " +str(node.leftNode.value))
                print("Right: "+ str(node.rightNode.content)+ ", " +str(node.rightNode.value))
            else:
                print("Leaf " + str(node.content))
            print("Hash: "+ node.value)
            print("")
            self._printRecursive(node.leftNode)
            self._printRecursive(node.rightNode)

    def _get_sibling(self, node):
        # Returns the node's sibling (parents other child)
        if node != None:
            if node.parent != None:
                if node.parent.leftNode == node:
                    # node is parent's left node, sibling on right
                    return node.parent.rightNode
                else:
                    # node is parent's right node, sibling on left
                    return node.parent.leftNode

    def get_path(self, value):
        # Returns an array of all strings to be hashed with initial value to get to the root
        valueNode = None # Identifies the node that contains the content == value
        returnstrings = [] # Merkle path
        for node in self.nodes:
            if node.content == value:  # Found a node with matching value
                valueNode = node
        if valueNode == None:
            if len(self.nodes) == 0:
                return "Tree is empty/uninitialized"
            return "No matching value in tree for " + str(value)
        while valueNode.parent != None:
            returnstrings.append(self._get_sibling(valueNode).value)
            valueNode = valueNode.parent
        return returnstrings
        

if __name__ == "__main__":
    """ Used for Testing """
    mtree = MerkleTree()
    for i in range(1,90): # Generates 70 nodes of values of single integers
        mtree.addNode(i)
    mtree.initialize()
    mtree.print_tree() # Tree information
    print("Root: "+ mtree.root.get_value()) # Root hash value
    hashed = sha1(str(5).encode()).hexdigest()
    for hash in mtree.get_path(5):
        print(hash)
        concatenated = str(int(hashed, 16) + int(hash, 16))
        hashed = sha1(concatenated.encode()).hexdigest()
    print("Proven: " + hashed) # Hash value given from hashing together path
    # if Proven and Root give the same integer, the system works!

    


    


                


