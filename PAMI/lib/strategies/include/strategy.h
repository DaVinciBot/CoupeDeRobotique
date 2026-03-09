#ifndef STRATEGIES_STRATEGY_H
#define STRATEGIES_STRATEGY_H

#include <Arduino.h>
#include <vector>
#include "action.h"
#include "rolling_basis.h"

/**
 * @brief Chef d'orchestre du robot : exécute séquentiellement une liste
 * d'actions (Carre, Triangle, AtoB, etc.).
 *
 * @note
 * - Les actions sont ajoutées via `addAction()` depuis `main.cpp`.
 * - Chaque action est responsable d'appeler `_rb->update()` dans son propre
 * `update()`.
 * - Strategy ne prend pas ownership des actions : ne pas les delete ici.
 */
class Strategy {
   public:
    /**
     * @brief Construit une Strategy vide.
     *
     * @param rb Pointeur vers le RollingBasis du robot (ne doit pas être nul).
     */
    explicit Strategy(RollingBasis* rb);

    /**
     * @brief Destructeur par défaut.
     *
     * @note Les actions ne sont pas supprimées ici : elles appartiennent à
     * l'appelant.
     */
    virtual ~Strategy() = default;

    /**
     * @brief Ajoute une action à la fin de la liste d'exécution.
     *
     * @param action Pointeur vers l'action à ajouter (ne doit pas être nul).
     *
     * @note Doit être appelé avant `start()`.
     *
     * @example
     * @code
     * strategy->addAction(new Carre(rb, 200, 0));
     * strategy->addAction(new Triangle(rb, 150, 0));
     * @endcode
     */
    void addAction(Action* action);

    /**
     * @brief Démarre la stratégie depuis la première action.
     *
     * @note Réinitialise l'index courant, `_finished` et `_failed`. Si la liste
     * est vide, passe directement à l'état terminé.
     */
    virtual void start();

    /**
     * @brief Met à jour l'action courante et avance dans la liste si elle est
     * terminée.
     *
     * @note Doit être appelé périodiquement dans `loop()`. Sans effet si
     * `isFinished()` ou `_failed` est vrai.
     */
    virtual void update();

    /**
     * @brief Stoppe immédiatement l'action courante et marque la stratégie
     * comme échouée.
     */
    virtual void stop();

    /**
     * @brief Indique si toutes les actions ont été exécutées avec succès.
     *
     * @return true  Toutes les actions sont terminées.
     * @return false Il reste des actions à exécuter.
     */
    virtual bool isFinished() const;

    /**
     * @brief Retourne le nom de la stratégie (pour les logs Serial).
     *
     * @return const char* Nom de la stratégie.
     */
    virtual const char* name() const { return "Strategy"; }

   protected:
    RollingBasis* _rb;              ///< Pointeur vers le rolling basis
    std::vector<Action*> _actions;  ///< Liste ordonnée des actions
    size_t _currentIndex;           ///< Index de l'action en cours
    bool _finished;                 ///< Vrai si toutes les actions sont faites
    bool _failed;                   ///< Vrai si stop() a été appelé

   private:
    /**
     * @brief Démarre l'action à l'index courant et loggue son nom.
     */
    void _startCurrentAction();
};

#endif