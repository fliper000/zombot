# Крутить рулетку в адмирал за 1 глазной суп
                item_count=self._get_game_state().count_in_storage('@R_60')
                if building_item.id == 'B_SOLDIER' and game_id == 'B_SOLDIER_ROULETTE' and item_count>=1:
                    self._get_game_state().remove_from_storage('@R_60',1)
                    play_cost = None
                # Конец адмирала
