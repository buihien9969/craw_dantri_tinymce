<?php

    use Illuminate\Database\Migrations\Migration;
    use Illuminate\Database\Schema\Blueprint;
    use Illuminate\Support\Facades\Schema;

    return new class extends Migration {

        /**
         * Run the migrations.
         */
        public function up(): void
        {
            Schema::create('article_views', function (Blueprint $table) {
                $table->id('view_id');
                $table->string('anonymous')->nullable();
                $table->unsignedBigInteger('article_id');
                $table->unsignedBigInteger('user_id')->nullable();
                $table->timestamp('viewed_at')->useCurrent();

                $table->foreign('article_id')
                    ->references('article_id')
                    ->on('articles')
                    ->onDelete('cascade');
                $table->foreign('user_id')
                    ->references('user_id')
                    ->on('users')
                    ->onDelete('set null');
            });
        }

        /**
         * Reverse the migrations.
         */
        public function down(): void
        {
            Schema::dropIfExists('article_views');
        }

    };
