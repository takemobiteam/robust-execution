import actionmodel.statespace as ss
import plancompilation.partialorderplan as pp
import plancompilation.extractminimalordering as mo


# Extract a Partial Order Plan:

def extract_partial_order_plan(plan_name: str, encoded_sequence: list[ss.Action]) -> tuple[pp.PartialOrderPlan, list[pp.Threat]]:
    # Abstracts a total order plan to a partial order plan.
    # Takes as input the encoded_sequence of a total order plan,
    # with start and end operators added.
    # Returns a partial order plan, composed of <actions, causal links, orderings>.

    actions = encoded_sequence  # The list is viewed as a set.
    links = extract_causal_links(plan_name, encoded_sequence)
    orderings, threats = extract_orderings(encoded_sequence,links)
    start_action = encoded_sequence[0] # start is 1st action of sequence
    partial_order_plan = pp.PartialOrderPlan(plan_name, actions, links, orderings, start_action)
    return partial_order_plan, threats


def extract_causal_links(plan_name: str, encoded_sequence: list[ss.Action]) -> list[pp.CausalLink]:
    # Extracts the goal / sub goal relationships of an encoded plan sequence,
    # in the form of “links” between operator preconditions and
    # effects that achieve these conditions.
    # Takes as input the encoded_sequence of a total order plan,
    # with start and end operators added.
    # Returns the complete set of causal links.

    causal_links: list[pp.CausalLink] = []
    active_links: list[pp.CausalLink] = []

    # Process actions from plan end to start,
    # constructing causal links by pairing each action precondition with a preceding action effect.
    # Also records action predecessors and successors according to the links.
    for action in reversed(encoded_sequence):
        # print()
        # print(f"Extracting Causal links for {action}.")

        # Note: no effect on the first pass, since no active links and
        # goal operator has no effects.
        for effect in action.effects:
            for link in active_links:
                if link.condition == effect:
                    link.producer = action
                    consumer = link.consumer
                    action.successor_links.append(link)
                    action.successor_actions.append(consumer)
                    consumer.predecessor_links.append(link)
                    consumer.predecessor_actions.append(action)
                    active_links.remove(link)
        for precondition in action.preconditions:
            link = pp.CausalLink(precondition,None, action)
            active_links.append(link)
            causal_links.append(link)

    # Warn that plan is incomplete (has open preconditions).
    if active_links:
        print()
        print(f"Missing producers for conditions in plan {plan_name}:")
        for link in active_links:
            print(f"condition {link.condition} of action {link.consumer} ")
    return causal_links


def extract_orderings(encoded_sequence: list[ss.Action], links: list[pp.CausalLink]) -> tuple[list[pp.Ordering], list[pp.Threat]]:
    # Given the causal links of an encoded plan sequence,
    # extract additional orderings needed to resolve potential threats.
    # An encoded_sequence is ill formed if it has a threat that can't be resolved
    # (an action with an effect that prevents a subsequent action from being invoked).
    # Returns a set of orderings and a set of unresolved threats.

    start = encoded_sequence[0]
    actions = encoded_sequence
    graph = mo.graph_for_actions_and_links(start, actions, links)

    orderings = []
    threats = []
    for link in links:
        condition = link.condition
        producer = link.producer
        consumer = link.consumer

        # For every threat, introduce an ordering that resolves the threat, consistent with the encoded sequence.

        for action in encoded_sequence:
            if effects_violate_condition(condition, action):
                # The effects of action could threaten the link.

                if action.location <= producer.location:
                    # If action appears before the producer in the grounded plan,
                    # then ensure that action precedes producer.
                    # Add this ordering if not already implied by the links.
                    if action != producer and not graph.path_exists(action, producer):
                        ordering = pp.Ordering(action, producer)
                        orderings.append(ordering)

                elif consumer.location <= action.location:
                    # If action appears after the consumer in the grounded plan,
                    # Ensure that action follows consumer, by adding an ordering if not implied by links.
                    if action != consumer and not graph.path_exists(consumer, action):
                        ordering = pp.Ordering(consumer, action)
                        orderings.append(ordering)

                else:
                    threat = pp.Threat(link, action)
                    threats.append(threat)

    # Remove any ordering that is implied by the causal links
    # and the (minimal) set of remaining orderings.
    minimal_orderings = mo.remove_dominated_orderings(graph, orderings)

    # For each action, record the actions that immediately precede or follow,
    # according to the minimal orderings.
    for ordering in minimal_orderings:
        predecessor = ordering.predecessor
        successor = ordering.successor
        successor.predecessor_actions.append(predecessor)
        predecessor.successor_actions.append(successor)

    return minimal_orderings, threats


def effects_violate_condition(condition: ss.Assignment, action: ss.Action) -> bool:
    # Return True if action has an effect with the same variable as condition, but a different value.
    cvar = condition.variable
    cval = condition.value
    for effect in action.effects:
        if effect.variable == cvar and effect.value != cval:
            return True
    return False

