class CoordsNode:
    def __init__(self, name, from_parent, to_parent, action=None):
        self.name = name
        self.nodes = {}
        self.from_parent = from_parent
        self.return_to_parent = to_parent
        self.action = action

    def add_node(self, node):
        name = node.name
        self.nodes[name] = node

    def navigate_to(self, destination: str):
        if destination == self.name:
            return self
        for child in self.nodes.values():
            if destination in child.return_all_nodes():
                child.from_parent()
                return child.navigate_to(destination)

        # destination not in child nodes
        raise Exception("Target node not a child of this node")

    def return_all_nodes(self):
        ret = [node.return_all_nodes() for node in self.nodes.values()]
        res = []
        for r in ret:
            res.extend(r)
        res.append(self.name)
        return res


class ArknightsCoords(CoordsNode):
    pass




