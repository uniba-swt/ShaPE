% description: a PROLOG meta interpreter simulating the semantics of separation
%              logic that searches for a determinisit set of rules describing a
%              memory graph, where a fresh variable in a rule must point to a
%              so far unconsumed node. The MI establishes a stateful execution,
%              where the state contains an input and output variable for:
%               - NIn, NOut: the nodes to be consumed
%               - RIn, ROut: the IDs of the rules applied so far
%               - CIn, COut: the IDs of the conditions of so far applied rules
% author: Jan H. Boockmann
% initially based on the vanilla MI from Markus Triska
%                     https://www.metalevel.at/acomip/ (accessed: 2019-08-23)


% The wrapper predicate to be invoked by the search script. Prints thes ID of
% each rule that is part of the found rules subset.
mi_seplog(G, NIn) :-
    mi_seplog(G, NIn, [], [], Rules, [], _),
    print(Rules).

% The atom true does not alter the state of the MI
mi_seplog(true, X, X, Y, Y, Z, Z).

% A compound term (A, B) is computed sequentially where the output of the first
% computation provides the input of the second computation.
mi_seplog((A, B), NIn, NOut, RIn, ROut, CIn, COut) :-
    mi_seplog(A,
              NIn,
              NOut1,
              RIn,
              ROut1,
              CIn,
              COut1),
    mi_seplog(B,
              NOut1,
              NOut,
              ROut1,
              ROut,
              COut1,
              COut),
    true.

% A clause statement does not alter the state of the MI and is evaluated as
%  usual.
mi_seplog(clause(A, B), X, X, Y, Y, Z, Z) :-
    clause(A, B),
    true.

% An inequality statement does not alter the state of the MI and is evaluated
% as usual.
mi_seplog(A\=B, X, X, Y, Y, Z, Z) :-
    A\=B,
    true.

% The node referenced by the node chunk must be consumable, i.e., inside the
% list of unconsumed nodes. Afterwards, the node is consumed and the remaining
% computation takes the updated list of consumable nodes as input.
mi_seplog(G, NIn, NOut, RIn, ROut, CIn, COut) :-
    G=node(X),
    member(X, NIn), % the node has not been consumed yet
    delete(NIn, X, NIn1), % consume the node
    clause(G, Body),
    mi_seplog(Body,
              NIn1,
              NOut,
              RIn,
              ROut,
              CIn,
              COut),
    true.

% A rule can be applied if it has been applied already, i.e., its ID is in the
% list of previously applied rules.
mi_seplog(G, NIn, NOut, RIn, ROut, CIn, COut) :-
    G=condition(Rule, _),
    member(Rule, RIn), % the rule has already been applied in the past
    clause(G, Body),
    mi_seplog(Body,
              NIn,
              NOut,
              RIn,
              ROut,
              CIn,
              COut),
    true.

% A rule can also be applied if it has not been applied yet, but no other rule
% of this condition group has been applied so far.
mi_seplog(G, NIn, NOut, RIn, ROut, CIn, COut) :-
    G=condition(Rule, Condition),
    \+ member(Rule, RIn), % the rule has not been applied in the past already
    \+ member(Condition, CIn), % no rule from this condition group has been applied so far
    append([Rule], RIn, RIn1),
    append([Condition], CIn, CIn1),
    clause(G, Body),
    mi_seplog(Body,
              NIn,
              NOut,
              RIn1,
              ROut,
              CIn1,
              COut),
    true.

% A node labeled as fresh must not have been consumed so far, i.e., it is in
% the list of consumable nodes
mi_seplog(G, NIn, NIn, RIn, RIn, CIn, CIn) :-
    G=fresh(X),
    member(X, NIn), % the node is still consumable
    true.

% If the current goal does not match any of the above handled cases, then
% evaluate the Body using the MI.
mi_seplog(G, NIn, NOut, RIn, ROut, CIn, COut) :-
    G\=true,
    G\=(_, _),
    G\=clause(_, _),
    G\=(_\=_),
    G\=node(_),
    G\=condition(_, _),
    G\=fresh(_),
    clause(G, Body),
    mi_seplog(Body,
              NIn,
              NOut,
              RIn,
              ROut,
              CIn,
              COut),
    true.
