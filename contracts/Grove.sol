contract Grove {
        /*
         *  Call tracking API
         */
        struct Node {
                bytes32 nodeId;
                bytes32 indexId;
                bytes32 id;
                int value;
                bytes32 parent;
                bytes32 left;
                bytes32 right;
                uint height;
        }

        // Maps an index id to the id of it's root node.
        mapping (bytes32 => bytes32) index_to_root;

        // Maps node_id to Node
        mapping (bytes32 => Node) node_lookup;

        // Map index_id to index Name
        mapping (bytes32 => bytes32) index_lookup;

        function getIndexId(address owner, bytes32 indexName) constant returns (bytes32) {
                return sha3(owner, indexName);
        }

        function getNodeId(bytes32 indexId, bytes32 id) constant returns (bytes32) {
                return sha3(indexId, id);
        }

        function max(uint a, uint b) internal returns (uint) {
            if (a >= b) {
                return a;
            }
            return b;
        }

        /*
         *  Node getters
         */
        function getIndexName(bytes32 indexId) constant returns (bytes32) {
            return index_lookup[indexId];
        }

        function getIndexRoot(bytes32 indexId) constant returns (bytes32) {
            return index_to_root[indexId];
        }

        function getNodeId(bytes32 nodeId) constant returns (bytes32) {
            return node_lookup[nodeId].id;
        }

        function getNodeIndexId(bytes32 nodeId) constant returns (bytes32) {
            return node_lookup[nodeId].indexId;
        }

        function getNodeValue(bytes32 nodeId) constant returns (int) {
            return node_lookup[nodeId].value;
        }

        function getNodeHeight(bytes32 nodeId) constant returns (uint) {
            return node_lookup[nodeId].height;
        }

        function getNodeParent(bytes32 nodeId) constant returns (bytes32) {
            return node_lookup[nodeId].parent;
        }

        function getNodeLeftChild(bytes32 nodeId) constant returns (bytes32) {
            return node_lookup[nodeId].left;
        }

        function getNodeRightChild(bytes32 nodeId) constant returns (bytes32) {
            return node_lookup[nodeId].right;
        }

        function getPreviousNode(bytes32 nodeId) constant returns (bytes32) {
            var currentNode = node_lookup[nodeId];

            if (currentNode.nodeId == 0x0) {
                // Unknown node, just return 0x0;
                return 0x0;
            }

            Node child;

            if (currentNode.left != 0x0) {
                // Trace left to latest child in left tree.
                child = node_lookup[currentNode.left];

                while (child.right != 0) {
                    child = node_lookup[child.right];
                }
                return child.nodeId;
            }

            if (currentNode.parent != 0x0) {
                // Now we trace back up through parent relationships, looking
                // for a link where the child is the right child of it's
                // parent.
                var parent = node_lookup[currentNode.parent];
                child = currentNode;

                while (true) {
                    if (parent.right == child.nodeId) {
                        return parent.nodeId;
                    }

                    if (parent.parent == 0x0) {
                        break;
                    }
                    child = parent;
                    parent = node_lookup[parent.parent];
                }
            }

            // This is the first node, and has no previous node.
            return 0x0;
        }

        function getNextNode(bytes32 nodeId) constant returns (bytes32) {
            var currentNode = node_lookup[nodeId];

            if (currentNode.nodeId == 0x0) {
                // Unknown node, just return 0x0;
                return 0x0;
            }

            Node child;

            if (currentNode.right != 0x0) {
                // Trace right to earliest child in right tree.
                child = node_lookup[currentNode.right];

                while (child.left != 0) {
                    child = node_lookup[child.left];
                }
                return child.nodeId;
            }

            if (currentNode.parent != 0x0) {
                // if the node is the left child of it's parent, then the
                // parent is the next one.
                var parent = node_lookup[currentNode.parent];
                child = currentNode;

                while (true) {
                    if (parent.left == child.nodeId) {
                        return parent.nodeId;
                    }

                    if (parent.parent == 0x0) {
                        break;
                    }
                    child = parent;
                    parent = node_lookup[parent.parent];
                }

                // Now we need to trace all the way up checking to see if any parent is the 
            }

            // This is the final node.
            return 0x0;
        }

        function insert(bytes32 indexName, bytes32 id, int value) public {
                bytes32 indexId = getIndexId(msg.sender, indexName);
                if (index_lookup[indexId] == 0x0) {
                    index_lookup[indexId] = indexName;
                }
                bytes32 nodeId = getNodeId(indexId, id);

                if (node_lookup[nodeId].nodeId == nodeId) {
                    // A node with this id already exists.  If the value is
                    // the same, then just return early, otherwise, remove it
                    // and reinsert it.
                    if (node_lookup[nodeId].value == value) {
                        return;
                    }
                    remove(indexName, id);
                }

                uint leftHeight;
                uint rightHeight;

                bytes32 previousNodeId = 0x0;

                bytes32 rootNodeId = index_to_root[indexId];

                if (rootNodeId == 0x0) {
                    rootNodeId = nodeId;
                    index_to_root[indexId] = nodeId;
                }
                var currentNode = node_lookup[rootNodeId];

                // Do insertion
                while (true) {
                    if (currentNode.indexId == 0x0) {
                        // This is a new unpopulated node.
                        currentNode.nodeId = nodeId;
                        currentNode.parent = previousNodeId;
                        currentNode.indexId = indexId;
                        currentNode.id = id;
                        currentNode.value = value;
                        break;
                    }

                    // Set the previous node id.
                    previousNodeId = currentNode.nodeId;

                    // The new node belongs in the right subtree
                    if (value >= currentNode.value) {
                        if (currentNode.right == 0x0) {
                            currentNode.right = nodeId;
                        }
                        currentNode = node_lookup[currentNode.right];
                        continue;
                    }

                    // The new node belongs in the left subtree.
                    if (currentNode.left == 0x0) {
                        currentNode.left = nodeId;
                    }
                    currentNode = node_lookup[currentNode.left];
                }

                // Rebalance the tree
                _rebalanceTree(currentNode.nodeId);
        }

        function exists(bytes32 indexId, bytes32 id) constant returns (bool) {
            bytes32 nodeId = getNodeId(indexId, id);
            return (node_lookup[nodeId].nodeId == nodeId);
        }

        function remove(bytes32 indexName, bytes32 id) public {
            bytes32 indexId = getIndexId(msg.sender, indexName);
            bytes32 nodeId = getNodeId(indexId, id);
            
            Node replacementNode;
            Node parent;
            Node child;
            bytes32 rebalanceOrigin;

            var nodeToDelete = node_lookup[nodeId];

            if (nodeToDelete.id != id) {
                // The id does not exist in the tree.
                return;
            }

            if (nodeToDelete.left != 0x0 || nodeToDelete.right != 0x0) {
                // This node is not a leaf node and thus must replace itself in
                // it's tree by either the previous or next node.
                if (nodeToDelete.left != 0x0) {
                    // This node is guaranteed to not have a right child.
                    replacementNode = node_lookup[getPreviousNode(nodeToDelete.nodeId)];
                }
                else {
                    // This node is guaranteed to not have a left child.
                    replacementNode = node_lookup[getNextNode(nodeToDelete.nodeId)];
                }
                // The replacementNode is guaranteed to have a parent.
                parent = node_lookup[replacementNode.parent];

                // Keep note of the location that our tree rebalancing should
                // start at.
                rebalanceOrigin = replacementNode.nodeId;

                // Join the parent of the replacement node with any subtree of
                // the replacement node.  We can guarantee that the replacement
                // node has at most one subtree because of how getNextNode and
                // getPreviousNode are used.
                if (parent.left == replacementNode.nodeId) {
                    parent.left = replacementNode.right;
                    if (replacementNode.right != 0x0) {
                        child = node_lookup[replacementNode.right];
                        child.parent = parent.nodeId;
                    }
                }
                if (parent.right == replacementNode.nodeId) {
                    parent.right = replacementNode.left;
                    if (replacementNode.left != 0x0) {
                        child = node_lookup[replacementNode.left];
                        child.parent = parent.nodeId;
                    }
                }

                // Now we replace the nodeToDelete with the replacementNode.
                // This includes parent/child relationships for all of the
                // parent, the left child, and the right child.
                replacementNode.parent = nodeToDelete.parent;
                if (nodeToDelete.parent != 0x0) {
                    parent = node_lookup[nodeToDelete.parent];
                    if (parent.left == nodeToDelete.nodeId) {
                        parent.left = replacementNode.nodeId;
                    }
                    if (parent.right == nodeToDelete.nodeId) {
                        parent.right = replacementNode.nodeId;
                    }
                }
                else {
                    // If the node we are deleting is the root node so update
                    // the indexId to root node mapping.
                    index_to_root[indexId] = replacementNode.nodeId;
                }

                replacementNode.left = nodeToDelete.left;
                if (nodeToDelete.left != 0x0) {
                    child = node_lookup[nodeToDelete.left];
                    child.parent = replacementNode.nodeId;
                }

                replacementNode.right = nodeToDelete.right;
                if (nodeToDelete.right != 0x0) {
                    child = node_lookup[nodeToDelete.right];
                    child.parent = replacementNode.nodeId;
                }
            }
            else if (nodeToDelete.parent != 0x0) {
                // The node being deleted is a leaf node so we only erase it's
                // parent linkage.
                parent = node_lookup[nodeToDelete.parent];

                if (parent.left == nodeToDelete.nodeId) {
                    parent.left = 0x0;
                }
                if (parent.right == nodeToDelete.nodeId) {
                    parent.right = 0x0;
                }

                // keep note of where the rebalancing should begin.
                rebalanceOrigin = parent.nodeId;
            }
            else {
                // This is both a leaf node and the root node, so we need to
                // unset the root node pointer.
                index_to_root[indexId] = 0x0;
            }

            // Now we zero out all of the fields on the nodeToDelete.
            nodeToDelete.id = 0x0;
            nodeToDelete.nodeId = 0x0;
            nodeToDelete.indexId = 0x0;
            nodeToDelete.value = 0;
            nodeToDelete.parent = 0x0;
            nodeToDelete.left = 0x0;
            nodeToDelete.right = 0x0;

            // Walk back up the tree rebalancing
            if (rebalanceOrigin != 0x0) {
                _rebalanceTree(rebalanceOrigin);
            }
        }

        bytes2 constant GT = ">";
        bytes2 constant LT = "<";
        bytes2 constant GTE = ">=";
        bytes2 constant LTE = "<=";
        bytes2 constant EQ = "==";

        function _compare(int left, bytes2 operator, int right) internal returns (bool) {
            if (operator == GT) {
                return (left > right);
            }
            if (operator == LT) {
                return (left < right);
            }
            if (operator == GTE) {
                return (left >= right);
            }
            if (operator == LTE) {
                return (left <= right);
            }
            if (operator == EQ) {
                return (left == right);
            }

            // Invalid operator.
            __throw();
        }

        function _getMaximum(bytes32 nodeId) internal returns (int) {
                var currentNode = node_lookup[nodeId];

                while (true) {
                    if (currentNode.right == 0x0) {
                        return currentNode.value;
                    }
                    currentNode = node_lookup[currentNode.right];
                }
        }

        function _getMinimum(bytes32 nodeId) internal returns (int) {
                var currentNode = node_lookup[nodeId];

                while (true) {
                    if (currentNode.left == 0x0) {
                        return currentNode.value;
                    }
                    currentNode = node_lookup[currentNode.left];
                }
        }

        function query(bytes32 indexId, bytes2 operator, int value) public returns (bytes32) {
                bytes32 rootNodeId = index_to_root[indexId];
                
                if (rootNodeId == 0x0) {
                    // Empty tree.
                    return 0x0;
                }

                var currentNode = node_lookup[rootNodeId];

                while (true) {
                    if (_compare(currentNode.value, operator, value)) {
                        // We have found a match but it might not be the
                        // *correct* match.
                        if ((operator == LT) || (operator == LTE)) {
                            // Need to keep traversing right until this is no
                            // longer true.
                            if (currentNode.right == 0x0) {
                                return currentNode.nodeId;
                            }
                            if (_compare(_getMinimum(currentNode.right), operator, value)) {
                                // There are still nodes to the right that
                                // match.
                                currentNode = node_lookup[currentNode.right];
                                continue;
                            }
                            return currentNode.nodeId;
                        }

                        if ((operator == GT) || (operator == GTE) || (operator == EQ)) {
                            // Need to keep traversing left until this is no
                            // longer true.
                            if (currentNode.left == 0x0) {
                                return currentNode.nodeId;
                            }
                            if (_compare(_getMaximum(currentNode.left), operator, value)) {
                                currentNode = node_lookup[currentNode.left];
                                continue;
                            }
                            return currentNode.nodeId;
                        }
                    }

                    if ((operator == LT) || (operator == LTE)) {
                        if (currentNode.left == 0x0) {
                            // There are no nodes that are less than the value
                            // so return null.
                            return 0x0;
                        }
                        currentNode = node_lookup[currentNode.left];
                        continue;
                    }

                    if ((operator == GT) || (operator == GTE)) {
                        if (currentNode.right == 0x0) {
                            // There are no nodes that are greater than the value
                            // so return null.
                            return 0x0;
                        }
                        currentNode = node_lookup[currentNode.right];
                        continue;
                    }

                    if (operator == EQ) {
                        if (currentNode.value < value) {
                            if (currentNode.right == 0x0) {
                                return 0x0;
                            }
                            currentNode = node_lookup[currentNode.right];
                            continue;
                        }

                        if (currentNode.value > value) {
                            if (currentNode.left == 0x0) {
                                return 0x0;
                            }
                            currentNode = node_lookup[currentNode.left];
                            continue;
                        }
                    }
                }
        }

        function _rebalanceTree(bytes32 nodeId) internal {
            // Trace back up rebalancing the tree and updating heights as
            // needed..
            var currentNode = node_lookup[nodeId];

            while (true) {
                int balanceFactor = _getBalanceFactor(currentNode.nodeId);

                if (balanceFactor == 2) {
                    // Right rotation (tree is heavy on the left)
                    if (_getBalanceFactor(currentNode.left) == -1) {
                        // The subtree is leaning right so it need to be
                        // rotated left before the current node is rotated
                        // right.
                        _rotateLeft(currentNode.left);
                    }
                    _rotateRight(currentNode.nodeId);
                }

                if (balanceFactor == -2) {
                    // Left rotation (tree is heavy on the right)
                    if (_getBalanceFactor(currentNode.right) == 1) {
                        // The subtree is leaning left so it need to be
                        // rotated right before the current node is rotated
                        // left.
                        _rotateRight(currentNode.right);
                    }
                    _rotateLeft(currentNode.nodeId);
                }

                if ((-1 <= balanceFactor) && (balanceFactor <= 1)) {
                    _updateNodeHeight(currentNode.nodeId);
                }

                if (currentNode.parent == 0x0) {
                    // Reached the root which may be new due to tree
                    // rotation, so set it as the root and then break.
                    break;
                }

                currentNode = node_lookup[currentNode.parent];
            }
        }

        function _getBalanceFactor(bytes32 nodeId) internal returns (int) {
                var node = node_lookup[nodeId];

                return int(node_lookup[node.left].height) - int(node_lookup[node.right].height);
        }

        function _updateNodeHeight(bytes32 nodeId) internal {
                var node = node_lookup[nodeId];

                node.height = max(node_lookup[node.left].height, node_lookup[node.right].height) + 1;
        }

        function _rotateLeft(bytes32 nodeId) internal {
            var originalRoot = node_lookup[nodeId];

            if (originalRoot.right == 0x0) {
                // Cannot rotate left if there is no right originalRoot to rotate into
                // place.
                __throw();
            }

            // The right child is the new root, so it gets the original
            // `originalRoot.parent` as it's parent.
            var newRoot = node_lookup[originalRoot.right];
            newRoot.parent = originalRoot.parent;

            // The original root needs to have it's right child nulled out.
            originalRoot.right = 0x0;

            if (originalRoot.parent != 0x0) {
                // If there is a parent node, it needs to now point downward at
                // the newRoot which is rotating into the place where `node` was.
                var parent = node_lookup[originalRoot.parent];

                // figure out if we're a left or right child and have the
                // parent point to the new node.
                if (parent.left == originalRoot.nodeId) {
                    parent.left = newRoot.nodeId;
                }
                if (parent.right == originalRoot.nodeId) {
                    parent.right = newRoot.nodeId;
                }
            }


            if (newRoot.left != 0) {
                // If the new root had a left child, that moves to be the
                // new right child of the original root node
                var leftChild = node_lookup[newRoot.left];
                originalRoot.right = leftChild.nodeId;
                leftChild.parent = originalRoot.nodeId;
            }

            // Update the newRoot's left node to point at the original node.
            originalRoot.parent = newRoot.nodeId;
            newRoot.left = originalRoot.nodeId;

            if (newRoot.parent == 0x0) {
                index_to_root[newRoot.indexId] = newRoot.nodeId;
            }

            // TODO: are both of these updates necessary?
            _updateNodeHeight(originalRoot.nodeId);
            _updateNodeHeight(newRoot.nodeId);
        }

        function _rotateRight(bytes32 nodeId) internal {
            var originalRoot = node_lookup[nodeId];

            if (originalRoot.left == 0x0) {
                // Cannot rotate right if there is no left node to rotate into
                // place.
                __throw();
            }

            // The left child is taking the place of node, so we update it's
            // parent to be the original parent of the node.
            var newRoot = node_lookup[originalRoot.left];
            newRoot.parent = originalRoot.parent;

            // Null out the originalRoot.left
            originalRoot.left = 0x0;

            if (originalRoot.parent != 0x0) {
                // If the node has a parent, update the correct child to point
                // at the newRoot now.
                var parent = node_lookup[originalRoot.parent];

                if (parent.left == originalRoot.nodeId) {
                    parent.left = newRoot.nodeId;
                }
                if (parent.right == originalRoot.nodeId) {
                    parent.right = newRoot.nodeId;
                }
            }

            if (newRoot.right != 0x0) {
                var rightChild = node_lookup[newRoot.right];
                originalRoot.left = newRoot.right;
                rightChild.parent = originalRoot.nodeId;
            }

            // Update the new root's right node to point to the original node.
            originalRoot.parent = newRoot.nodeId;
            newRoot.right = originalRoot.nodeId;

            if (newRoot.parent == 0x0) {
                index_to_root[newRoot.indexId] = newRoot.nodeId;
            }

            // Recompute heights.
            _updateNodeHeight(originalRoot.nodeId);
            _updateNodeHeight(newRoot.nodeId);
        }

        function __throw() internal {
            int[] x;
            x[1];
        }
}
